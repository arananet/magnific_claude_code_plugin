---
name: magnific-creator-workflows
description: Use when the user wants to create, enhance, or reuse visual assets with Magnific — upscaling or enhancing an image, generating images or video from a prompt, removing a background, building a repeatable character or style reference, generating speech or a 3D model, or finding something they made before. Triggers on "upscale", "enhance", "make this print-ready", "4K/8K", "generate an image", "generate a video", "remove the background", "same character", "keep the style", "my past creations", "Magnific", or when a creator hands over a rough render, product shot, thumbnail, or key frame and asks to make it usable.
---

# Magnific for content creators

This is a community-built integration, not an official Magnific product.
It talks to Magnific's public MCP endpoint using the user's own account.

Magnific is reached through the `magnific` MCP server (`https://mcp.magnific.com`).
It is the creative step, not a code step: the user is producing an asset someone
will look at. Treat quality, consistency, and cost as the things that matter.

## Before anything else

**Check the live tool list.** Tool names below reflect Magnific's documentation at
the time of writing; the server is the authority. Read the tools the `magnific`
server actually advertises in this session and match by purpose, not by the exact
name printed here. If a name differs, use the live one and keep going — do not
tell the user the plugin is broken.

**Authentication is OAuth, not an API key.** The first Magnific tool call opens a
browser sign-in for the user's Magnific account; Claude Code stores the session.
Never ask for, generate, or write a Magnific API key, and never add one to
`.mcp.json` or the environment — the REST API uses keys, this endpoint does not.
If a call fails with an auth error, tell the user to re-run the sign-in (see
`/magnific:setup`), not to supply a key.

**Generations cost credits.** Every image, video, upscale, TTS, and 3D generation
draws on the user's Magnific credit balance, scaled by model and resolution.
Before the first paid call in a session, say in one line what you are about to run
and that it spends credits. Do not fire a batch of variations on your own
initiative — produce one, show it, then iterate on request.

## Picking the tool

| The creator wants | Reach for |
| --- | --- |
| More resolution, more detail, print- or broadcast-ready | `images_upscale` |
| An image from a prompt, or an edit of an existing image | `images_generate` |
| A cutout / transparent PNG for compositing | `images_remove_background` |
| Motion from a prompt or a still | `video_generate` |
| The same character, product, or look across many assets | `custom_references_create`, then pass the reference |
| Voiceover or narration | `audio_tts` |
| A 3D asset | `models3d_generate` |
| "the one I made last week", a starting point from past work | `creations_search`, then `creations_show` |
| To see what this account can actually do | `tools_show` |

When the ask is ambiguous between generating new and improving existing, ask one
question rather than guessing — regenerating an asset the creator already approved
is the expensive mistake.

## Upscaling is a creative choice, not a resize

Magnific's upscaler invents plausible detail. That is the point, and it is also the
risk. Match the mode to the job:

- **Faithful work** — product shots, real people, packaging, anything a client will
  compare against the original. Stay conservative; invented detail on a real product
  is a defect. The precision models exist for this.
- **Generative work** — concept art, illustration, an AI render that only has to look
  good. Let it hallucinate detail; that is where the "magic" reputation comes from.

Always ask which side of that line the asset sits on when it isn't obvious, and tell
the user what you chose. On faces, hands, text, and logos, review the result before
calling it done — those are where an upscaler's invented detail shows first.

## Consistency across a set

When a creator needs more than one asset that belong together (a campaign, a series
of thumbnails, a character in several scenes), build a reference first with
`custom_references_create` and reuse it, instead of re-prompting from scratch each
time and hoping. Prompt-only consistency drifts; a reference is the mechanism.

## The plugin's local tooling

This plugin adds machinery around the MCP server. Use it — it is why reaching for
Magnific here is different from calling the API.

- **Every result is captured.** A PostToolUse hook downloads returned assets to
  `.magnific/assets/` and records the tool, prompt, and settings in
  `.magnific/ledger.jsonl`. Hosted URLs expire; the local copy does not. Tell the
  user the local path, not just the link.
- **Spend is guarded.** A PreToolUse hook asks for confirmation once the day's
  paid-call budget is used. If it asks, stop and surface it — never work around it.
- **The ledger is searchable offline**:
  `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/magnific/report.py" library <terms>`,
  `... provenance <file>` for what produced a given file, and `... budget` for spend.
  Check the library before generating: the asset may already exist.
- **Multi-asset work goes to the `magnific-art-director` subagent**, which plans the
  set, anchors it to one reference, and reviews each result before spending on the next.

The guard counts paid *tool calls*, not credits — it cannot see the real balance.
Say that plainly if the user asks; don't imply it tracks their account.

## Working with the results

- Give the user both the hosted URL and the local path the capture hook saved.
- Generated media is large — `.magnific/assets/` is gitignored by default. Do not
  commit assets unless the user explicitly asks.
- Prefer finding a past asset over regenerating one: the local ledger first, then
  `creations_search` for work made before this plugin or in another client.

## Don't

- Don't run a paid generation to "check if it works" — use `tools_show` or ask.
- Don't silently upscale to the maximum resolution; higher costs more and is often
  not what the deliverable needs. Ask what it is for (web, print, video) and size to that.
- Don't produce likenesses of real, identifiable people on request without the user
  confirming they have the rights, and don't generate content that misrepresents a
  real person or brand.
