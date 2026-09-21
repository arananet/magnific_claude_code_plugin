#!/usr/bin/env python3
"""PostToolUse hook: keep every Magnific result.

Magnific returns hosted URLs that expire. Without this, a creator's best
result is a link in a scrolled-away transcript. This downloads the asset next
to the project and records what produced it, so the work is reproducible and
searchable offline.
"""

import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from magnific import lib  # noqa: E402

TIMEOUT = 60


def asset_name(url: str, tool: str, index: int) -> str:
    stem = url.split("?", 1)[0].rsplit("/", 1)[-1] or "asset"
    suffix = Path(stem).suffix or ".bin"
    short = tool.split("__")[-1] or "magnific"
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    return f"{stamp}-{short}-{index}{suffix}"


def download(url: str, dest: Path, max_mb: int) -> str:
    """Save one asset. Returns a status string; never raises."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "magnific-claude-plugin"})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            length = resp.headers.get("Content-Length")
            if length and int(length) > max_mb * 1024 * 1024:
                return f"skipped (>{max_mb}MB)"
            data = resp.read(max_mb * 1024 * 1024 + 1)
    except (urllib.error.URLError, OSError, ValueError) as exc:
        return f"not downloaded ({type(exc).__name__})"
    if len(data) > max_mb * 1024 * 1024:
        return f"skipped (>{max_mb}MB)"
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
    except OSError as exc:
        return f"not saved ({type(exc).__name__})"
    return "saved"


def summarize_input(tool_input) -> dict:
    """The few fields worth remembering, truncated. The ledger is a trail,
    not a copy of the request."""
    if not isinstance(tool_input, dict):
        return {}
    keep = ("prompt", "mode", "model", "scale", "resolution", "reference", "style", "image", "url")
    out = {}
    for k, v in tool_input.items():
        if k.lower() in keep and isinstance(v, (str, int, float, bool)):
            out[k] = str(v)[:400]
    return out


def main() -> None:
    data = lib.read_hook_input()
    tool = data.get("tool_name", "")
    lib.set_project_root(data.get("cwd"))
    lib.debug_log("capture invoked for tool=" + repr(tool))
    if not lib.is_magnific_tool(tool):
        lib.emit({})
        return

    try:
        cfg = lib.config()
        response = data.get("tool_response", "")
        urls = lib.extract_asset_urls(response)
        # A result is often returned as a link to its page on Magnific rather
        # than to the file, so record those too instead of losing the creation.
        creations = lib.extract_creation_urls(response)
        saved, notes = [], []

        if urls and cfg.get("auto_download"):
            base = lib.project_root() / cfg["asset_dir"]
            for i, url in enumerate(urls, 1):
                dest = base / asset_name(url, tool, i)
                status = download(url, dest, int(cfg["max_download_mb"]))
                if status == "saved":
                    saved.append(str(dest.relative_to(lib.project_root())))
                else:
                    notes.append(f"{url}: {status}")

        if not urls and not creations:
            lib.emit({})
            return

        lib.append_ledger({
            "at": lib.utc_now(),
            "tool": tool,
            "paid": lib.is_paid_tool(tool),
            "input": summarize_input(data.get("tool_input")),
            "urls": urls,
            "creations": creations,
            "files": saved,
            "session": data.get("session_id", ""),
        })

        lines = [f"Magnific: recorded {len(urls) + len(creations)} result(s) in "
                 ".magnific/ledger.jsonl."]
        if saved:
            lines.append("Saved locally: " + ", ".join(saved))
        if notes:
            lines.append("Not saved: " + "; ".join(notes))
        if creations and not saved:
            lines.append(
                "The result came back as a Magnific page link (" + creations[0] + "), "
                "not a direct file, so there is nothing to download automatically. "
                "If the user wants a local copy, ask Magnific for the asset URL or "
                "download it from that page.")
        lib.emit({"hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": " ".join(lines),
        }})
    except Exception:
        lib.emit({})


if __name__ == "__main__":
    main()
