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

As a plugin (gets the commands and the skill too):

```bash
/plugin install arananet/magnific_claude_code_plugin
```

Or register just the MCP server:

```bash
claude mcp add --transport http magnific https://mcp.magnific.com
```

## Authentication

**OAuth, not an API key.** The first Magnific tool call opens a Magnific sign-in
in your browser; approve it and Claude Code keeps the session. There is nothing
to paste and no key to store — do not add credentials to `.mcp.json`.
(Magnific's REST API does use API keys; that is a separate surface this plugin
does not touch.)

Generations spend credits from your Magnific balance, scaled by model and
resolution.

## What you get

| Command | Does |
| --- | --- |
| `/magnific:setup` | Connect the server and explain the OAuth sign-in |
| `/magnific:upscale` | Upscale an asset, faithful or generative, sized to the deliverable |
| `/magnific:generate` | Generate an image or video, with reference-based consistency |
| `/magnific:creations` | Search your history and reuse a past asset |

Plus the `magnific-creator-workflows` skill, which fires on natural requests
("make this print-ready", "same character, different scene", "the one I made last
week") and picks the right Magnific tool, guards credit spend, and keeps a set of
assets visually consistent.

The underlying MCP server exposes tools for upscaling, image and video generation,
background removal, custom references, creation search, text-to-speech, and 3D
generation. The skill reads the server's live tool list rather than hardcoding
names, so it keeps working if Magnific adds or renames tools.

## Develop

```bash
bash setup.sh          # install git hooks
bash tests/plugin.sh   # plugin contract tests (no network, no account needed)
bash scripts/openspec check
```

---

## Usage

Once installed, just ask:

- "Upscale `hero.png` for a print poster" → picks the faithful path, sizes to print
- "Generate a thumbnail with this character" → builds or reuses a reference
- "Find the product shot I made last week and cut out the background"

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
