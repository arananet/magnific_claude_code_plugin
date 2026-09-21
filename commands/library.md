---
description: Search your local Magnific ledger — what you made, what produced it, where it is on disk
argument-hint: [search terms, or a filename for provenance]
---

Search the local record of Magnific work: $ARGUMENTS

Run:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/magnific/report.py" library $ARGUMENTS
```

If the argument looks like a file path or filename, run `provenance` instead to
show exactly which tool, prompt, and settings produced that file.

This reads `.magnific/ledger.jsonl`, written locally by the capture hook every
time a Magnific tool returns — so it works offline and covers assets whose
hosted URLs have since expired. Present the results as a short list: what it is,
when, and the local path.

If the ledger is empty, say so and offer `creations_search` against the Magnific
account instead — that covers work made before this plugin was installed, or
from another client.
