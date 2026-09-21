# magnific_claude_code_plugin

![Claude Code](https://img.shields.io/badge/Claude%20Code-plugin-8A4FFF) ![MCP](https://img.shields.io/badge/MCP-streamable%20HTTP-informational) ![OpenSpec](https://img.shields.io/badge/OpenSpec-enforced-blueviolet) ![License](https://img.shields.io/badge/License-MIT-green)

> A Claude Code plugin that brings Magnific's creative AI — upscaling, image and
> video generation, character/style references, and your creation history — into
> a normal Claude Code session.

**Unofficial.** This is a community-built integration by a fan of the platform,
not affiliated with or endorsed by Magnific. It talks to Magnific's public MCP
endpoint using your own account and credits.

---

## Install

This repo is its own marketplace, so add it first, then install from it:

```bash
/plugin marketplace add arananet/magnific_claude_code_plugin
/plugin install magnific@arananet
```

`/plugin install arananet/magnific_claude_code_plugin` does **not** work —
`/plugin install` takes `plugin@marketplace`, not a repo path, and reports
`Marketplace ... not found`.

## Authentication

**OAuth, not an API key.** The first Magnific tool call opens a Magnific sign-in
in your browser; approve it and Claude Code keeps the session. There is nothing
to paste and no key to store — do not add credentials to `.mcp.json`.
(Magnific's REST API does use API keys; that is a separate surface this plugin
does not touch.)

Generations spend credits from your Magnific balance, scaled by model and
resolution.

## What you get

Registering the MCP server is one line. The plugin is the tooling around it.

### Spend guard (PreToolUse hook)

Magnific generations cost credits, and an agent in a loop or a batch pointed at
the wrong folder can burn a balance in seconds. Before any paid Magnific call the
guard checks the day's paid-call count and asks for confirmation once the budget
is used. Read-only tools (`creations_search`, `tools_show`) are never guarded. A
Magnific tool the plugin doesn't recognize is treated as **paid** — fail closed,
so a newly added generation tool is guarded on day one.

It counts paid *tool calls*, not credits: no local hook can see your real
balance. It's a rate limit against runaway spend, not accounting.

### Asset ledger (PostToolUse hook)

Magnific returns hosted URLs that expire. Every result is downloaded to
`.magnific/assets/` and recorded in `.magnific/ledger.jsonl` along with the tool,
prompt, and settings that produced it — so your best result isn't a dead link in
a scrolled-away transcript, and you can answer "what made this?" months later.

Both hooks exit 0 on any error. A bookkeeping failure never breaks your tool call.

### Commands

| Command | Does |
| --- | --- |
| `/magnific:setup` | Connect the server and explain the OAuth sign-in |
| `/magnific:upscale` | Upscale an asset, faithful or generative, sized to the deliverable |
| `/magnific:generate` | Generate an image or video, with reference-based consistency |
| `/magnific:batch` | Run an operation over a folder — confirms the file list, runs one first, then goes sequentially |
| `/magnific:brief` | Turn a creative brief into a consistent asset set |
| `/magnific:library` | Search the local ledger, or trace what produced a file |
| `/magnific:budget` | Spend against budget; change the limit |
| `/magnific:creations` | Search your Magnific account history |

### Subagent

`magnific-art-director` runs multi-asset productions: checks budget and existing
work first, anchors the set to one custom reference instead of re-prompting (which
drifts), generates one asset at a time, and reviews each before spending on the next.

### Skill

`magnific-creator-workflows` fires on natural requests — "make this print-ready",
"same character, different scene", "the one I made last week" — and picks the tool
from the server's **live** tool list rather than a hardcoded set, so it keeps
working when Magnific adds or renames tools. It also encodes the judgment calls:
faithful vs. generative upscaling, reference-based consistency, checking the
library before regenerating.

### Configuration

`.magnific/config.json`, all optional:

```json
{
  "daily_paid_call_budget": 25,
  "confirm_every_paid_call": false,
  "auto_download": true,
  "asset_dir": ".magnific/assets",
  "max_download_mb": 50
}
```

## Develop

```bash
bash setup.sh                          # install git hooks
bash tests/plugin.sh                   # contract tests — no network, no account needed
python3 tests/magnific_hooks_test.py   # hook logic unit tests
bash scripts/openspec check
```

Hook scripts are standard-library Python 3 under `scripts/magnific/`. Hook config
lives in `plugin-hooks/` because the repo root's `hooks/` already holds OpenSpec's
git hooks.

---

## Usage

You don't call tools by name — describe the asset and the skill routes it. These
are real phrasings, with what each one triggers.

### Generate images

```text
Generate a hero image for a landing page: a ceramic coffee cup on a dark
walnut table, morning window light from the left, 16:9
```

```text
Make three thumbnail concepts for a video about AI upscaling — bold, high
contrast, readable at 200px wide
```

Claude generates **one** first and shows it, rather than spending on three
concepts you may hate. Say "the second direction, warmer" and it iterates.

```text
Take product.jpg and put it on a marble surface with soft studio lighting,
keep the label exactly as it is
```

### Generate video

```text
Turn this still into a 5-second shot: slow push-in, subtle steam rising
from the cup
```

```text
Generate a 10-second B-roll clip of rain on a city window at night, moody,
no people, 9:16 for a reel
```

Video is the most expensive thing here. Claude states the cost before running
and won't generate variants unprompted. Ask for the aspect ratio you actually
need — regenerating for a different crop costs full price.

### Upscale and enhance

```text
Upscale hero.png for a 60x40cm print
```

Claude asks — or infers — whether this is *faithful* or *generative* work:

```text
Upscale this client's product photo. Stay true to the source, it's going
next to the real product on the packaging
```

```text
Upscale this concept sketch for a pitch deck — go wild with the detail,
nothing here has to match reality
```

That distinction matters more than resolution. An upscaler invents plausible
detail; on a real product that's a defect, on concept art it's the point.

```text
Enhance this 2013 phone photo of the storefront enough to use as a website
header
```

### Keep a set consistent

The thing prompts alone can't do:

```text
I need 8 images of the same character — a woman in a red raincoat — in
different city locations. Keep her face and coat identical across all of them
```

This goes to the `magnific-art-director` subagent: it builds **one** custom
reference first, then generates against it, instead of re-prompting eight times
and getting eight different people.

```text
Build a style reference from these three images, then use it for every asset
in the campaign
```

### Batch a folder

```text
/magnific:batch ./product-shots upscale all of these for the web store
```

Claude lists the files and the count, waits for your confirmation, runs **one**
first so you can check the settings, then processes the rest sequentially. A
wrong setting across 40 images is the failure mode this prevents.

```text
/magnific:batch ./cutouts/*.jpg remove the backgrounds
```

### Run a brief

```text
/magnific:brief We're launching a cold brew can in three flavors. I need a
hero shot per flavor, a 9:16 story version of each, and one 15-second loop
for the ad. Same can, same lighting, different colorways.
```

The art director reads it back, checks your budget against the asset count,
anchors everything to one reference, and generates one at a time with a review
between each.

### Audio and 3D

```text
Generate a voiceover for this script, calm and warm, mid-pace
```

```text
Generate a 3D model of this product shot so I can spin it in the promo
```

### Find and reuse what you already made

```text
/magnific:library red raincoat
```

```text
What produced .magnific/assets/20260921-images_upscale-1.png?
```

Shows the exact tool, prompt and settings behind that file — months later, after
the hosted URL has expired.

```text
Find the cup shot I made last week and generate a 9:16 version of it
```

Reusing costs nothing and keeps the look consistent. Claude checks the local
ledger before generating something new.

### Watch the spend

```text
/magnific:budget
```

```text
/magnific:budget 60
```

Raises the daily paid-call limit. The guard asks for confirmation once you hit
it — useful precisely when an agent is mid-batch and you've stopped watching.
It counts paid **tool calls**, not credits; for your real balance, check your
Magnific account.

---

## Contributing

This project uses **OpenSpec** for spec-driven development — every feature
or bugfix starts with a spec file under `.openspec/specs/`. Each spec
includes a `roles` block to assign responsibility (`implementer`,
`reviewer`, `qa`, `product_owner`). See
[`docs/OPENSPEC.md`](docs/OPENSPEC.md) for the full workflow, or
[`CONTRIBUTING.md`](CONTRIBUTING.md) for the contributor checklist.

For small projects, use one concise spec and focused tests; no extra plan
document or specialist is required. Roles are responsibilities, not a minimum
team size. See [incremental adoption](docs/ADOPTION.md) for optional enterprise
capabilities and known enforcement limits. AI spec review is opt-in.

The OpenSpec CLI and hooks require Bash, Git and Ruby >= 2.6 (no gems).
Run `bash scripts/openspec verify <slug>` to record test evidence and
`bash scripts/openspec status` to inspect freshness. Manual work needs no AI
runtime; bounded agent execution is separately opt-in. See [execution](docs/EXECUTION.md).

---

## Documentation

| Topic | Where |
| --- | --- |
| Spec-driven workflow | [`docs/OPENSPEC.md`](docs/OPENSPEC.md) |
| Small-project adoption and assessment | [`docs/ADOPTION.md`](docs/ADOPTION.md) |
| Guided project setup | [`docs/ONBOARDING.md`](docs/ONBOARDING.md) |
| Branch protection setup | [`docs/BRANCH_PROTECTION.md`](docs/BRANCH_PROTECTION.md) |
| Architecture decisions | [`docs/adr/`](docs/adr/) |
| Security policy | [`SECURITY.md`](SECURITY.md) |
| Support channels | [`SUPPORT.md`](SUPPORT.md) |
| Release history | [`CHANGELOG.md`](CHANGELOG.md) |

---

## License

[MIT](LICENSE)

---

## Developer

Eduardo Arana

## Support this with a ko-fi

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/H2H51MPWG)
