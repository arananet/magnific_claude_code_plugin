#!/usr/bin/env python3
"""Read the local Magnific ledger: spend so far, and what produced what.

    report.py budget            spend against the configured budget
    report.py library [query]   recorded assets, newest first
    report.py provenance <file> what produced a given local file
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from magnific import lib  # noqa: E402


def cmd_budget() -> int:
    cfg, entries = lib.config(), lib.read_ledger()
    day = lib.paid_calls_since(entries, 24)
    week = lib.paid_calls_since(entries, 24 * 7)
    budget = cfg["daily_paid_call_budget"]
    print(f"Paid Magnific calls, last 24h: {len(day)}/{budget}")
    print(f"Paid Magnific calls, last 7d:  {len(week)}")
    print(f"Ledger entries total:          {len(entries)}")
    by_tool = {}
    for e in week:
        by_tool[e.get("tool", "?")] = by_tool.get(e.get("tool", "?"), 0) + 1
    if by_tool:
        print("\nLast 7 days by tool:")
        for tool, n in sorted(by_tool.items(), key=lambda kv: -kv[1]):
            print(f"  {n:>4}  {tool.split('__')[-1]}")
    if budget and len(day) >= budget:
        print("\nBudget reached — the guard hook will ask before the next paid call.")
    return 0


def matches(entry: dict, query: str) -> bool:
    if not query:
        return True
    hay = " ".join([
        entry.get("tool", ""),
        " ".join(entry.get("files", [])),
        " ".join(entry.get("urls", [])),
        " ".join(entry.get("creations", [])),
        " ".join(f"{k}={v}" for k, v in (entry.get("input") or {}).items()),
    ]).lower()
    return all(term in hay for term in query.lower().split())


def cmd_library(query: str) -> int:
    hits = [e for e in reversed(lib.read_ledger()) if matches(e, query)]
    if not hits:
        print("No recorded creations match." if query else "The ledger is empty.")
        return 0
    for e in hits[:40]:
        prompt = (e.get("input") or {}).get("prompt", "")
        print(f"{e.get('at', '?')}  {e.get('tool', '?').split('__')[-1]}")
        if prompt:
            print(f"    prompt: {prompt[:160]}")
        for f in e.get("files", []):
            print(f"    file:   {f}")
        for u in e.get("urls", [])[:3]:
            print(f"    url:    {u}")
        for c in e.get("creations", [])[:3]:
            print(f"    page:   {c}")
    if len(hits) > 40:
        print(f"\n... and {len(hits) - 40} more")
    return 0


def cmd_provenance(needle: str) -> int:
    for e in reversed(lib.read_ledger()):
        if any(needle in f for f in e.get("files", [])):
            print(f"at:    {e.get('at')}")
            print(f"tool:  {e.get('tool')}")
            for k, v in (e.get("input") or {}).items():
                print(f"{k + ':':<7}{v}")
            for u in e.get("urls", []):
                print(f"url:   {u}")
            for c in e.get("creations", []):
                print(f"page:  {c}")
            return 0
    print(f"No ledger entry records {needle}.")
    return 1


def main(argv: list) -> int:
    cmd = argv[0] if argv else "budget"
    if cmd == "budget":
        return cmd_budget()
    if cmd == "library":
        return cmd_library(" ".join(argv[1:]))
    if cmd == "provenance":
        if len(argv) < 2:
            print("usage: report.py provenance <file>", file=sys.stderr)
            return 2
        return cmd_provenance(argv[1])
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
