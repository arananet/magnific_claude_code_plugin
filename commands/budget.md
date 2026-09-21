---
description: Show Magnific spend against your local budget, or change it
argument-hint: [new daily paid-call budget]
---

Report Magnific spend: $ARGUMENTS

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/magnific/report.py" budget
```

If the user passed a number, update `daily_paid_call_budget` in
`.magnific/config.json` (creating the file if needed, preserving other keys) and
confirm the new value.

Explain the model honestly when it's relevant: the guard counts **paid tool
calls**, not credits. It cannot see the user's real Magnific credit balance —
no local hook can. It is a rate limit against runaway spend (an agent looping,
a batch pointed at the wrong folder), not an accounting system. For the actual
balance, point them at their Magnific account.

Other settings in `.magnific/config.json`: `confirm_every_paid_call`,
`auto_download`, `asset_dir`, `max_download_mb`.
