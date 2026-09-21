#!/usr/bin/env python3
"""PreToolUse hook: stop a runaway Magnific spend before it happens.

Magnific generations cost credits. An agent looping over variations, or a
batch command pointed at the wrong folder, can burn a balance in seconds.
This asks for confirmation once the day's paid-call budget is used up.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from magnific import lib  # noqa: E402


def decide(tool_name: str, cfg: dict, entries: list):
    """Return (decision, reason) or (None, None) to stay out of the way."""
    if not lib.is_magnific_tool(tool_name) or not lib.is_paid_tool(tool_name):
        return None, None

    recent = lib.paid_calls_since(entries, hours=24)
    used, budget = len(recent), cfg["daily_paid_call_budget"]

    if cfg.get("confirm_every_paid_call"):
        return "ask", (
            f"{tool_name} spends Magnific credits. Confirmation is required for "
            f"every paid call (confirm_every_paid_call is on). {used} paid call(s) "
            "in the last 24h."
        )

    if budget and used >= budget:
        return "ask", (
            f"Magnific daily budget reached: {used}/{budget} paid calls in the last "
            f"24h. {tool_name} would spend more credits. Raise "
            "daily_paid_call_budget in .magnific/config.json, or confirm this one."
        )

    return None, None


def main() -> None:
    data = lib.read_hook_input()
    tool_name = data.get("tool_name", "")
    lib.set_project_root(data.get("cwd"))
    lib.debug_log("guard invoked for tool=" + repr(tool_name))
    try:
        decision, reason = decide(tool_name, lib.config(), lib.read_ledger())
    except Exception:  # never break the user's tool call over bookkeeping
        decision, reason = None, None

    out = {"hookEventName": "PreToolUse"}
    if decision:
        out["permissionDecision"] = decision
        out["permissionDecisionReason"] = reason
    lib.emit({"hookSpecificOutput": out})


if __name__ == "__main__":
    main()
