---
description: Generate an image or video with Magnific from a prompt
argument-hint: <prompt> [--video] [--reference <name>]
---

Generate the asset the user described: $ARGUMENTS

Follow the `magnific-creator-workflows` skill. Specifically:

- Pick `images_generate` or `video_generate` from what was asked; don't assume video
  unless motion was requested.
- If this asset belongs to a set that needs a consistent character, product, or look,
  build or reuse a reference (`custom_references_create`) instead of relying on the
  prompt alone — prompt-only consistency drifts across a series.
- Tighten a thin prompt by asking one question about the thing that actually matters
  (subject, aspect ratio, intended use), not by padding it with adjectives on your own.
- State the credit cost in one line, generate **one** result, show it, then iterate
  only on request. Do not fan out variations unprompted.
- Return the asset URL. Save to disk only if the user asked for a file.
