---
description: Diagnose why Magnific hooks, the ledger, or downloads are not working
---

Work out what is actually wired up. Report findings plainly; fix nothing without asking.

1. **Is the MCP server connected?** Check whether Magnific tools are available in
   this session. If not, the plugin may be installed but unauthenticated — the
   first tool call opens the browser OAuth flow.

2. **Are the hooks loaded?** `/plugin` or `/reload-plugins` reports a hook count.
   **0 hooks means nothing is being captured or guarded** — the MCP server still
   works, but results are not saved and spend is not limited. If it reports 0,
   the plugin needs updating — the hook config ships inside it:

   ```text
   /plugin marketplace update arananet
   /plugin uninstall magnific@arananet
   /plugin install magnific@arananet
   ```

   Then restart Claude Code and check `/reload-plugins` again.

3. **Did the hooks actually fire?** Turn on logging by writing
   `{"debug": true}` into `.magnific/config.json` (preserve existing keys), run
   one Magnific tool, then read `.magnific/hook-debug.log`. Each line records the
   tool name the hook was invoked with.

   - No log file at all → the hooks are not loaded (step 2).
   - Lines present but no ledger entry → the tool name did not look like
     Magnific, or the response carried no links. Report the exact tool name from
     the log; that is what the matcher needs to cover.

4. **Is anything recorded?** Run
   `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/magnific/report.py" library` and
   `... budget`. Report what is and isn't there.

5. **Why is nothing downloading?** Magnific often returns a link to the
   creation's *page* (`magnific.com/app/creation/<id>`) rather than to the file.
   That page cannot be fetched as an image, so the ledger records the link but
   saves no file — check the entry's `creations` field. A direct media URL (one
   ending in `.png`, `.mp4`, …) is what gets downloaded. This is expected
   behaviour, not a failure.

Finish with a short list: what works, what doesn't, and the single next step.
