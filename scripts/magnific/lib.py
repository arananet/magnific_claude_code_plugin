"""Shared helpers for the Magnific plugin's hooks and commands.

Everything here is local: the plugin keeps a per-project ledger of what
Magnific produced so a creator can answer "what made this?" and "what have I
spent today?" without a network round trip. Standard library only.
"""

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# Tools that cost credits. Kept as patterns, not an exhaustive list, so a
# renamed or newly added generation tool is still caught.
PAID_PATTERNS = (
    r"upscale",
    r"generate",
    r"_tts\b",
    r"remove_background",
)

# Tools that only read. Never guarded, never counted.
FREE_PATTERNS = (
    r"creations_(search|show|get|list)",
    r"tools_show",
)

DEFAULTS = {
    # Paid calls allowed per rolling day before the guard asks for confirmation.
    "daily_paid_call_budget": 25,
    # Ask before every paid call, regardless of budget.
    "confirm_every_paid_call": False,
    # Where downloaded assets land, relative to the project root.
    "asset_dir": ".magnific/assets",
    # Download returned asset URLs to disk automatically.
    "auto_download": True,
    # Skip downloads above this size (MB). Video gets large fast.
    "max_download_mb": 50,
}


def project_root() -> Path:
    """The directory the plugin stores state in.

    Claude Code sets CLAUDE_PROJECT_DIR for hooks; fall back to cwd so the
    scripts stay runnable by hand and in tests.
    """
    return Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())


def state_dir() -> Path:
    return project_root() / ".magnific"


def config() -> dict:
    cfg = dict(DEFAULTS)
    path = state_dir() / "config.json"
    try:
        user = json.loads(path.read_text())
    except (OSError, ValueError):
        return cfg
    if isinstance(user, dict):
        cfg.update({k: v for k, v in user.items() if k in DEFAULTS})
    return cfg


def ledger_path() -> Path:
    return state_dir() / "ledger.jsonl"


def read_ledger() -> list:
    """Every recorded entry. A corrupt line is skipped, never fatal — the
    ledger is a convenience, and losing the session over it would be worse."""
    entries = []
    try:
        raw = ledger_path().read_text()
    except OSError:
        return entries
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except ValueError:
            continue
    return entries


def append_ledger(entry: dict) -> None:
    path = ledger_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def is_magnific_tool(name: str) -> bool:
    return bool(name) and "magnific" in name.lower()


def is_paid_tool(name: str) -> bool:
    """Paid unless it matches a known read-only tool.

    Deliberately fail-closed: an unrecognized Magnific tool is treated as paid,
    so a new generation tool gets guarded on day one instead of spending
    silently.
    """
    low = (name or "").lower()
    if any(re.search(p, low) for p in FREE_PATTERNS):
        return False
    return any(re.search(p, low) for p in PAID_PATTERNS) or is_magnific_tool(low)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def paid_calls_since(entries: list, hours: int = 24) -> list:
    cutoff = datetime.now(timezone.utc).timestamp() - hours * 3600
    recent = []
    for e in entries:
        if not e.get("paid"):
            continue
        try:
            ts = datetime.fromisoformat(e["at"]).timestamp()
        except (KeyError, ValueError):
            continue
        if ts >= cutoff:
            recent.append(e)
    return recent


def read_hook_input() -> dict:
    try:
        return json.loads(sys.stdin.read() or "{}")
    except ValueError:
        return {}


def emit(payload: dict) -> None:
    """Hook output. Always valid JSON on stdout, always exit 0 — a hook that
    crashes the tool call is worse than a hook that does nothing."""
    json.dump(payload, sys.stdout)
    sys.stdout.write("\n")


URL_RE = re.compile(r"https?://[^\s\"'<>)\]]+", re.IGNORECASE)
ASSET_EXT = (
    ".png", ".jpg", ".jpeg", ".webp", ".gif", ".avif", ".tiff",
    ".mp4", ".webm", ".mov", ".mp3", ".wav", ".glb", ".gltf", ".obj",
)


def extract_asset_urls(blob) -> list:
    """Asset URLs in an arbitrary tool response.

    Walks whatever structure came back rather than assuming a schema, because
    the response shape is Magnific's to change.
    """
    text = blob if isinstance(blob, str) else json.dumps(blob, ensure_ascii=False)
    seen, urls = set(), []
    for url in URL_RE.findall(text):
        url = url.rstrip(".,;")
        path = url.split("?", 1)[0].lower()
        if not path.endswith(ASSET_EXT):
            continue
        if url in seen:
            continue
        seen.add(url)
        urls.append(url)
    return urls
