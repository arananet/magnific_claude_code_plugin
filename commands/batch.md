---
description: Run a Magnific operation across a folder of images, one at a time, within budget
argument-hint: <folder or glob> <what to do — upscale for print, remove backgrounds, ...>
---

Batch Magnific work over: $ARGUMENTS

This is where credits get burned by accident, so work carefully.

1. **Resolve the file list first and show it.** Use Glob. Report the count and
   the total, and get explicit confirmation before the first paid call. Never
   start a batch on an unconfirmed file list.
2. **Check the budget** with
   `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/magnific/report.py" budget`.
   If the batch is larger than what remains, say so and propose either a smaller
   subset or raising the budget — let the user choose.
3. **Run the first file alone.** Show the result and confirm the settings are
   right before processing the rest. One wrong setting across 40 images is the
   expensive failure mode this step exists to prevent.
4. **Then process sequentially**, not in parallel. Report progress as you go.
   Stop immediately and report if a call fails twice or the spend guard asks for
   confirmation.
5. **Summarize**: input file, output path, anything that needs a human eye. The
   capture hook has already saved each result under `.magnific/assets/` and
   recorded it in the ledger.

If the user hasn't said what the assets are for, ask before starting — print,
web, and video want different resolutions, and the wrong one means running the
whole batch again.
