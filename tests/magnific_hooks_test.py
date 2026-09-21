#!/usr/bin/env python3
"""Unit tests for the Magnific plugin's hook logic. Standard library only."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from magnific import lib, guard  # noqa: E402

GUARD = ROOT / "scripts" / "magnific" / "guard.py"
CAPTURE = ROOT / "scripts" / "magnific" / "capture.py"
REPORT = ROOT / "scripts" / "magnific" / "report.py"


def run_hook(script: Path, payload: dict, project_dir: str) -> dict:
    env = dict(os.environ, CLAUDE_PROJECT_DIR=project_dir)
    proc = subprocess.run(
        [sys.executable, str(script)], input=json.dumps(payload),
        capture_output=True, text=True, env=env, timeout=30,
    )
    assert proc.returncode == 0, f"{script.name} exited {proc.returncode}: {proc.stderr}"
    return json.loads(proc.stdout or "{}")


class ToolClassification(unittest.TestCase):
    def test_generation_tools_are_paid(self):
        for name in ("mcp__magnific__images_upscale", "mcp__magnific__images_generate",
                     "mcp__magnific__video_generate", "mcp__magnific__audio_tts",
                     "mcp__magnific__models3d_generate"):
            self.assertTrue(lib.is_paid_tool(name), name)

    def test_read_only_tools_are_free(self):
        for name in ("mcp__magnific__creations_search", "mcp__magnific__creations_show",
                     "mcp__magnific__creations_get", "mcp__magnific__tools_show"):
            self.assertFalse(lib.is_paid_tool(name), name)

    def test_unknown_magnific_tool_is_treated_as_paid(self):
        # Fail closed: a tool Magnific adds tomorrow gets guarded today.
        self.assertTrue(lib.is_paid_tool("mcp__magnific__some_future_thing"))

    def test_namespaced_plugin_tool_names_are_recognized(self):
        # A plugin-provided server is namespaced; the session shows it as
        # plugin:magnific:magnific, so the bare mcp__magnific__ form is not
        # what arrives.
        name = "mcp__plugin:magnific:magnific__images_generate"
        self.assertTrue(lib.is_magnific_tool(name))
        self.assertTrue(lib.is_paid_tool(name))

    def test_non_magnific_tools_are_ignored(self):
        self.assertFalse(lib.is_magnific_tool("Bash"))
        self.assertFalse(lib.is_magnific_tool("mcp__github__get_me"))


class UrlExtraction(unittest.TestCase):
    def test_finds_media_urls_and_ignores_page_links(self):
        resp = {"content": [{"type": "text", "text":
                "Result: https://cdn.magnific.com/out/a1.png and "
                "https://cdn.magnific.com/out/clip.mp4?sig=abc . Docs: https://magnific.com/docs"}]}
        urls = lib.extract_asset_urls(resp)
        self.assertEqual(urls, ["https://cdn.magnific.com/out/a1.png",
                                "https://cdn.magnific.com/out/clip.mp4?sig=abc"])

    def test_deduplicates(self):
        blob = "https://x.test/a.png https://x.test/a.png"
        self.assertEqual(lib.extract_asset_urls(blob), ["https://x.test/a.png"])

    def test_handles_a_plain_string_response(self):
        self.assertEqual(lib.extract_asset_urls("done: https://x.test/b.webp"),
                         ["https://x.test/b.webp"])

    def test_no_urls_is_empty_not_an_error(self):
        self.assertEqual(lib.extract_asset_urls({"ok": True}), [])


class CreationLinks(unittest.TestCase):
    """Results often come back as a link to the creation's page, not the file."""

    PAGE = "https://www.magnific.com/app/creation/YMvSdInWeC"

    def test_creation_page_is_captured(self):
        self.assertEqual(lib.extract_creation_urls({"text": f"Done: {self.PAGE}"}), [self.PAGE])

    def test_creation_page_is_not_mistaken_for_a_downloadable_asset(self):
        self.assertEqual(lib.extract_asset_urls({"text": self.PAGE}), [])

    def test_ordinary_magnific_links_are_not_creations(self):
        self.assertEqual(lib.extract_creation_urls({"text": "https://www.magnific.com/docs"}), [])


class GuardDecisions(unittest.TestCase):
    def setUp(self):
        self.cfg = dict(lib.DEFAULTS)

    def ledger(self, n, hours_ago=1):
        from datetime import datetime, timedelta, timezone
        at = (datetime.now(timezone.utc) - timedelta(hours=hours_ago)).isoformat(timespec="seconds")
        return [{"at": at, "paid": True, "tool": "mcp__magnific__images_generate"} for _ in range(n)]

    def test_under_budget_stays_out_of_the_way(self):
        decision, _ = guard.decide("mcp__magnific__images_generate", self.cfg, self.ledger(3))
        self.assertIsNone(decision)

    def test_at_budget_asks(self):
        self.cfg["daily_paid_call_budget"] = 5
        decision, reason = guard.decide("mcp__magnific__images_generate", self.cfg, self.ledger(5))
        self.assertEqual(decision, "ask")
        self.assertIn("5/5", reason)

    def test_old_calls_fall_out_of_the_window(self):
        self.cfg["daily_paid_call_budget"] = 5
        decision, _ = guard.decide("mcp__magnific__images_generate", self.cfg,
                                   self.ledger(9, hours_ago=30))
        self.assertIsNone(decision)

    def test_free_tools_are_never_guarded_even_over_budget(self):
        self.cfg["daily_paid_call_budget"] = 1
        decision, _ = guard.decide("mcp__magnific__creations_search", self.cfg, self.ledger(50))
        self.assertIsNone(decision)

    def test_confirm_every_call_always_asks(self):
        self.cfg["confirm_every_paid_call"] = True
        decision, _ = guard.decide("mcp__magnific__images_generate", self.cfg, [])
        self.assertEqual(decision, "ask")

    def test_non_magnific_tool_is_untouched(self):
        self.cfg["daily_paid_call_budget"] = 0
        decision, _ = guard.decide("Bash", self.cfg, self.ledger(99))
        self.assertIsNone(decision)


class HookProcesses(unittest.TestCase):
    """The hooks must always exit 0 with valid JSON — a crashing hook would
    break the user's tool call, which is worse than doing nothing."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="magnific-test-")

    def test_guard_emits_valid_json(self):
        out = run_hook(GUARD, {"tool_name": "mcp__magnific__images_generate"}, self.tmp)
        self.assertEqual(out["hookSpecificOutput"]["hookEventName"], "PreToolUse")

    def test_guard_survives_garbage_input(self):
        env = dict(os.environ, CLAUDE_PROJECT_DIR=self.tmp)
        proc = subprocess.run([sys.executable, str(GUARD)], input="not json",
                              capture_output=True, text=True, env=env, timeout=30)
        self.assertEqual(proc.returncode, 0)
        json.loads(proc.stdout)

    def test_capture_writes_a_ledger_entry(self):
        payload = {
            "tool_name": "mcp__magnific__images_upscale",
            "tool_input": {"prompt": "product shot", "mode": "faithful", "nonsense": {"deep": 1}},
            "tool_response": {"content": [{"text": "https://x.invalid/never-resolves.png"}]},
            "session_id": "s1",
        }
        run_hook(CAPTURE, payload, self.tmp)
        entries = [json.loads(l) for l in
                   (Path(self.tmp) / ".magnific" / "ledger.jsonl").read_text().splitlines()]
        self.assertEqual(len(entries), 1)
        e = entries[0]
        self.assertTrue(e["paid"])
        self.assertEqual(e["input"]["prompt"], "product shot")
        self.assertNotIn("nonsense", e["input"])          # only known fields kept
        self.assertEqual(e["urls"], ["https://x.invalid/never-resolves.png"])
        self.assertEqual(e["files"], [])                   # download failed, entry still recorded

    def test_capture_records_a_page_link_when_there_is_no_file(self):
        payload = {
            "tool_name": "mcp__plugin:magnific:magnific__images_generate",
            "tool_input": {"prompt": "ceramic cup"},
            "tool_response": {"content": [{"text":
                "Done. https://www.magnific.com/app/creation/YMvSdInWeC"}]},
            "cwd": self.tmp,
        }
        out = run_hook(CAPTURE, payload, "/nonexistent-project-dir")
        entry = json.loads((Path(self.tmp) / ".magnific" / "ledger.jsonl").read_text().strip())
        self.assertEqual(entry["creations"], ["https://www.magnific.com/app/creation/YMvSdInWeC"])
        self.assertEqual(entry["files"], [])
        self.assertIn("page link", out["hookSpecificOutput"]["additionalContext"])

    def test_payload_cwd_wins_so_a_plain_folder_works(self):
        # The working directory need not be a git repo, and CLAUDE_PROJECT_DIR
        # may point elsewhere; state belongs where the tool call happened.
        payload = {
            "tool_name": "mcp__plugin:magnific:magnific__images_generate",
            "tool_response": "https://www.magnific.com/app/creation/ABC",
            "cwd": self.tmp,
        }
        run_hook(CAPTURE, payload, "/nonexistent-project-dir")
        self.assertTrue((Path(self.tmp) / ".magnific" / "ledger.jsonl").is_file())

    def test_capture_ignores_non_magnific_tools(self):
        run_hook(CAPTURE, {"tool_name": "Bash", "tool_response": "https://x.test/a.png"}, self.tmp)
        self.assertFalse((Path(self.tmp) / ".magnific" / "ledger.jsonl").exists())

    def test_report_runs_against_an_empty_project(self):
        env = dict(os.environ, CLAUDE_PROJECT_DIR=self.tmp)
        proc = subprocess.run([sys.executable, str(REPORT), "budget"],
                              capture_output=True, text=True, env=env, timeout=30)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("last 24h", proc.stdout)


class LedgerRobustness(unittest.TestCase):
    def test_corrupt_lines_are_skipped_not_fatal(self):
        tmp = tempfile.mkdtemp(prefix="magnific-test-")
        d = Path(tmp) / ".magnific"
        d.mkdir()
        (d / "ledger.jsonl").write_text('{"at":"x","paid":true}\nnot json\n\n{"at":"y"}\n')
        old = os.environ.get("CLAUDE_PROJECT_DIR")
        os.environ["CLAUDE_PROJECT_DIR"] = tmp
        try:
            self.assertEqual(len(lib.read_ledger()), 2)
        finally:
            if old is None:
                del os.environ["CLAUDE_PROJECT_DIR"]
            else:
                os.environ["CLAUDE_PROJECT_DIR"] = old


if __name__ == "__main__":
    unittest.main(verbosity=1)
