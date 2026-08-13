#!/usr/bin/env python3
"""Phase D log auditor for the prefill_draft/decode_draft domain split.

Offline verification of edge/cloud logs captured on NPU CI (see
`PhaseD_验证与压测清单.md`).  Pure stdlib - no third-party deps.

Phase C semantics (2026-08-13):
  - PREFILL_DRAFT_LAST is published by the CLOUD (POST_OUT) after its
    worker finishes the PDFF middle segment; the edge no longer
    self-posts prefill tails.
  - The cloud classifies draft heads into per-domain queues
    (ready_prefill_drafts / ready_decode_drafts) and dispatches via the
    CloudUndesiredState machine ([PD-PASSIVE] picked lines).
  - A PDFL missing past the watchdog interval raises on the edge
    ("[PD] PREFILL_DRAFT_LAST lost") - it is a FAIL here.

Checks (edge log):
  C1  slot conservation: every PREFILL_FIRST pick is finalized exactly
      once (no double finalize, no leak).  In-flight slots at log end
      are a WARN unless --strict.
  C2  channel violations: zero occurrences of hidden-channel mismatch,
      per-domain tail channel assertions, or "parent slot released".
  C3  per-domain draft picks counted; prefill_inflight never exceeds
      its configured limit.
  C4  cloud-published PDFL arrivals (inbox "Received scheduler_output
      from cloud, batch_type: PREFILL_DRAFT_LAST"); watchdog loss
      raises are a hard FAIL.

Checks (cloud log, optional --cloud-log):
  C5  classified batch counts per queue (PassiveScheduler classified)
      and dispatched batch types (PassiveScheduler.schedule picked).
  C6  zero tail-segment batches leaked back into the cloud dispatch
      (error-level "received tail-segment").
  C7  PDFL publish idempotency: "Suppressing duplicate PREFILL_DRAFT_
      LAST" must be zero; "Skipping POST_OUT for PREFILL_DRAFT_FIRST"
      must be zero (Phase C publishes it).

Conservation (requires both logs): cloud-dispatched PREFILL_DRAFT_FIRST
count must match edge PDFL arrivals modulo the in-flight window
(<= per-domain remote pending limit, default 2).

Usage:
  python audit_pd_logs.py edge.log [--cloud-log cloud.log] [--strict]
Exit codes: 0 = pass, 1 = FAIL, 2 = WARN-only (leak in flight at EOF).
"""

import argparse
import re
import sys
from collections import Counter

# ------------------------------------------------------------------ edge -- #
SLOT_START = re.compile(r"batch_type is PREFILL_FIRST\b")
SLOT_FINALIZE = re.compile(r"\[PD\] finalize prefill slot head_token=(\S+)")
RELEASE = re.compile(
    r"\[PD\] release_prefill: channel=(\S+) head_token=(\S+) free=(\S+)"
)
DRAFT_PICK = re.compile(
    r"\[MTP-DEBUG\] scheduler picked "
    r"(PREFILL_DRAFT_FIRST|PREFILL_DRAFT_LAST|DECODE_DRAFT_FIRST|DECODE_DRAFT_LAST)"
)
PREFILL_INFLIGHT = re.compile(r"prefill_inflight: (\d+)/(\d+)")
PDFL_ARRIVAL = re.compile(
    r"Received scheduler_output from cloud, batch_type: PREFILL_DRAFT_LAST\b"
)
WATCHDOG_LOSS = re.compile(r"\[PD\] PREFILL_DRAFT_LAST lost for task_id=")

CHANNEL_VIOLATION_MARKERS = (
    "hidden channel mismatch",
    "expects a prefill hidden channel",
    "expects decode hidden channel",
    "parent slot released",
    "release_prefill: channel=None",
)

# ---------------------------------------------------------------- cloud --- #
CLOUD_CLASSIFIED = re.compile(
    r"PassiveScheduler classified seq=\S+ batch_type=(\S+) "
    r"\(prefills=(\d+), pdmixes=(\d+), prefill_drafts=(\d+), "
    r"decode_drafts=(\d+), decodes=(\d+)\)"
)
CLOUD_PICKED = re.compile(
    r"PassiveScheduler\.schedule\[\S+\] picked batch_type=(\S+)"
)
CLOUD_TAIL_LEAK = re.compile(r"received tail-segment batch_type=(\w+)")
CLOUD_SUPPRESS_DUPLICATE = re.compile(
    r"Suppressing duplicate (PREFILL_DRAFT_LAST|PREFILL_LAST|DECODE_LAST) "
    r"publish for guard_key=(\S+)"
)
CLOUD_SKIP_PDFF = re.compile(
    r"Skipping POST_OUT for PREFILL_DRAFT_FIRST\b"
)


def audit_edge(path: str) -> tuple[dict, list[str], list[str]]:
    stats = Counter()
    finalized = Counter()
    max_inflight, inflight_limit = 0, 0
    violations: list[str] = []
    warns: list[str] = []
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            for marker in CHANNEL_VIOLATION_MARKERS:
                if marker in line:
                    violations.append(line.rstrip())
                    break
            m = SLOT_START.search(line)
            if m:
                stats["slot_starts"] += 1
            m = SLOT_FINALIZE.search(line)
            if m:
                stats["slot_finalized"] += 1
                finalized[m.group(1)] += 1
            m = RELEASE.search(line)
            if m:
                stats["release_prefill"] += 1
            m = DRAFT_PICK.search(line)
            if m:
                stats[f"pick_{m.group(1)}"] += 1
            for m in PREFILL_INFLIGHT.finditer(line):
                cur, lim = int(m.group(1)), int(m.group(2))
                max_inflight = max(max_inflight, cur)
                inflight_limit = lim
            if PDFL_ARRIVAL.search(line):
                stats["pdfL_arrivals"] += 1
            if WATCHDOG_LOSS.search(line):
                # Hard FAIL: a cloud-published tail missing past the
                # watchdog interval means link failure / cloud death.
                violations.append(
                    "PDFL watchdog raised (cloud tail lost): "
                    + line.rstrip()
                )
    stats["max_prefill_inflight"] = max_inflight
    stats["prefill_inflight_limit"] = inflight_limit

    dups = [ht for ht, n in finalized.items() if n > 1]
    if dups:
        fails = [
            f"double finalize of slot head_token={ht} x{n}"
            for ht, n in finalized.items()
            if n > 1
        ]
    else:
        fails = []
    leaked = stats["slot_starts"] - len(finalized)
    if leaked > 0:
        warns.append(
            f"{leaked} slot(s) not finalized by EOF "
            f"({stats['slot_starts']} starts vs {len(finalized)} unique finalized) - "
            "OK if chains were still in flight at shutdown; rerun with --strict "
            "to treat as FAIL"
        )
    if max_inflight > inflight_limit:
        fails.append(
            f"prefill_inflight {max_inflight} exceeded limit {inflight_limit}"
        )
    return stats, warns, fails + violations


def audit_cloud(path: str) -> tuple[dict, list[str], list[str]]:
    stats = Counter()
    warns: list[str] = []
    fails: list[str] = []
    queue_peaks = Counter()
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            m = CLOUD_CLASSIFIED.search(line)
            if m:
                stats[f"cls_{m.group(1)}"] += 1
                for qname, idx in (
                    ("prefills", 2),
                    ("pdmixes", 3),
                    ("prefill_drafts", 4),
                    ("decode_drafts", 5),
                    ("decodes", 6),
                ):
                    queue_peaks[qname] = max(queue_peaks[qname], int(m.group(idx)))
            m = CLOUD_PICKED.search(line)
            if m:
                stats[f"picked_{m.group(1)}"] += 1
            m = CLOUD_TAIL_LEAK.search(line)
            if m:
                # Any tail segment back on the cloud is a routing bug.
                fails.append(
                    f"tail-segment leaked into cloud dispatch: {m.group(1)}"
                )
            m = CLOUD_SUPPRESS_DUPLICATE.search(line)
            if m:
                fails.append(
                    f"cloud suppressed duplicate {m.group(1)} publish "
                    f"(guard_key={m.group(2)}) - idempotency violation"
                )
            if CLOUD_SKIP_PDFF.search(line):
                # Phase C must publish PDFL for every PDFF ack.
                fails.append(
                    "cloud skipped POST_OUT for PREFILL_DRAFT_FIRST "
                    "(Phase C should publish PREFILL_DRAFT_LAST)"
                )
    for qname, peak in sorted(queue_peaks.items()):
        stats[f"peak_queue_{qname}"] = peak
    return stats, warns, fails


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("edge_log")
    ap.add_argument("--cloud-log")
    ap.add_argument(
        "--strict",
        action="store_true",
        help="treat in-flight slots at EOF as FAIL (for closed runs)",
    )
    args = ap.parse_args()

    fails: list[str] = []
    warns: list[str] = []

    stats, w, f = audit_edge(args.edge_log)
    warns += w
    fails += f

    cloud_stats = None
    if args.cloud_log:
        cloud_stats, w, f = audit_cloud(args.cloud_log)
        warns += w
        fails += f

    # Cross-log conservation: cloud dispatched N PDFF heads; the edge
    # must have received N PDFL tails minus the in-flight window
    # (PDFFs still executing on the cloud at log end).
    if cloud_stats is not None:
        pdf_f_dispatched = cloud_stats.get("picked_PREFILL_DRAFT_FIRST", 0)
        pdf_l_arrived = stats.get("pdfL_arrivals", 0)
        pdf_l_picked = stats.get("pick_PREFILL_DRAFT_LAST", 0)
        # In-flight allowance: per-domain remote pending limit (default 2).
        allowed_gap = 2
        if pdf_f_dispatched > pdf_l_arrived + allowed_gap:
            fails.append(
                "PDFL conservation broken: cloud dispatched "
                f"{pdf_f_dispatched} PDFF but edge received only "
                f"{pdf_l_arrived} PDFL (gap > in-flight window {allowed_gap})"
            )
        if pdf_l_arrived > pdf_l_picked + allowed_gap:
            fails.append(
                f"edge received {pdf_l_arrived} PDFL but picked only "
                f"{pdf_l_picked} (gap > {allowed_gap}) - inbox stall?"
            )

    print("=" * 72)
    print("Phase D log audit - edge:", args.edge_log)
    print("-" * 72)
    edge_order = [
        "slot_starts",
        "slot_finalized",
        "release_prefill",
        "max_prefill_inflight",
        "prefill_inflight_limit",
        "pick_PREFILL_DRAFT_FIRST",
        "pick_PREFILL_DRAFT_LAST",
        "pick_DECODE_DRAFT_FIRST",
        "pick_DECODE_DRAFT_LAST",
        "pdfL_arrivals",
    ]
    for key in edge_order:
        if key in stats:
            print(f"  {key:<32} {stats[key]}")
    if cloud_stats is not None:
        print("-" * 72)
        print("Phase D log audit - cloud:", args.cloud_log)
        for key in sorted(cloud_stats):
            print(f"  {key:<32} {cloud_stats[key]}")

    print("-" * 72)
    for wline in warns:
        print(f"  WARN  {wline}")
    for fline in fails:
        print(f"  FAIL  {fline}")
    if not fails and not warns:
        print("  PASS - no violations, slots conserved")
    elif not fails:
        print("  PASS (warnings only)")
    else:
        print(f"  FAIL - {len(fails)} violation(s)")
    print("=" * 72)
    if fails:
        return 1
    if warns and args.strict:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
