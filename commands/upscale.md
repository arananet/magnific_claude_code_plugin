---
description: Upscale or enhance an image with Magnific
argument-hint: <image path or URL> [what it's for — print, web, video]
---

Upscale the asset the user named: $ARGUMENTS

Follow the `magnific-creator-workflows` skill. Specifically:

- Establish whether this is **faithful** work (real product, real person, client
  comparison — stay true to the source) or **generative** work (concept art,
  illustration — let the model invent detail). Ask if it isn't clear from the asset
  or the stated use.
- Size to the actual deliverable. Ask what it's for rather than defaulting to the
  maximum resolution; higher costs more credits and is often not what's needed.
- Say what you're about to run and that it spends credits, then run one upscale.
- When it returns, give the user the asset URL and flag anything to check —
  faces, hands, text, and logos are where invented detail shows first.

If the user gave no image, ask for one, or offer to find a recent asset with
`creations_search`.
