# Changelog

All notable changes to `magnific_claude_code_plugin` will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Historical dates below are Git author dates, not release dates. Uncommitted
changes remain undated under `Unreleased`.

<!--
Guidelines:
- Add a new entry under `## [Unreleased]` as you work — no batching up for release day.
- Group entries under: Added, Changed, Deprecated, Removed, Fixed, Security.
- Reference the spec slug and PR number:  "Added dark mode (spec: dark-mode, #42)".
- On release, rename `[Unreleased]` to the new version with the release date,
  and open a fresh `[Unreleased]` section at the top.
- The release-drafter workflow auto-populates draft release notes from PRs —
  keep PR titles tidy so they flow straight into here.
-->

## [Unreleased]

### Added

- Magnific Claude Code plugin: `magnific` MCP server (streamable HTTP, browser
  OAuth) plus eight slash commands — `setup`, `upscale`, `generate`, `batch`,
  `brief`, `library`, `budget`, `creations` — and the
  `magnific-creator-workflows` skill (spec: magnific-mcp-plugin).
- PreToolUse spend guard: asks for confirmation once the daily paid-call budget
  is reached, never guards read-only tools, and treats an unrecognized Magnific
  tool as paid (spec: magnific-mcp-plugin).
- PostToolUse asset capture: downloads returned assets to `.magnific/assets/`
  and records tool, prompt, settings and paths in `.magnific/ledger.jsonl`,
  searchable offline via `scripts/magnific/report.py` (spec: magnific-mcp-plugin).
- `magnific-art-director` subagent for multi-asset productions
  (spec: magnific-mcp-plugin).
- Tests: `tests/plugin.sh` contract checks (manifest, transport and url, no
  credentials in config, hook wiring, frontmatter) and
  `tests/magnific_hooks_test.py` unit tests for tool classification, URL
  extraction, guard decisions, ledger writes and malformed-input handling
  (spec: magnific-mcp-plugin).

### Added

- README usage examples covering image and video generation, faithful vs.
  generative upscaling, reference-based consistency across a set, folder
  batches, briefs, audio and 3D, library and provenance lookups, and the spend
  guard (spec: magnific-mcp-plugin).

### Fixed

- The repo was not installable: `/plugin install arananet/magnific_claude_code_plugin`
  failed with `Marketplace "arananet/magnific_claude_code_plugin" not found`,
  because `/plugin install` takes `plugin@marketplace` and the repo carried no
  marketplace manifest. Added `.claude-plugin/marketplace.json`, corrected the
  install instructions in README and `/magnific:setup` to the two-step form, and
  added tests that fail if the marketplace manifest or the documented install
  command regresses (spec: magnific-mcp-plugin).

- Installation was rejected with `agents: Invalid input`: the manifest declared
  `commands`, `agents` and `skills` as directory strings, but the schema takes
  arrays there. Removed all three — those directories are auto-discovered at the
  plugin root — and added a test that fails if a non-list value reappears
  (spec: magnific-mcp-plugin).

### Changed

- Onboarded the OpenSpec template into this project: filled config values,
  removed template-internal specs and the template marker, and rewrote the
  README around the plugin (spec: magnific-mcp-plugin).

### Added

- Shared local/CI Markdown lint runner with locked dependencies, `make setup-lint`, `make lint-markdown`, and `make verify-template` (spec: lean-agent-workflow).
- Persistent verification evidence, stale-state detection, pause/resume and optional bounded local agent adapters (spec: reliable-verification-and-resumable-execution).

### Changed

- README starts with one minimal adoption path; agent check and auto-fix instructions follow the shared CLI and readiness contract (spec: lean-agent-workflow).
- Markdown lint uses CLI 0.23.2 with a patched TOML parser; table spacing follows its new default rule without changing security policies (spec: lean-agent-workflow).
- CLI, hooks and deterministic CI share a Ruby standard-library YAML engine; Ruby >= 2.6 is now required. `make test name=<slug>` verifies the selected spec.
- Downstream checks reject missing/unconfigured config; template maintenance uses an explicit marker removed during adoption.

### Fixed

- Markdown formatting errors in agent instructions and project documentation, preserving lint rules and policy content (spec: enterprise-hardening).
- Markdown lint CI now passes a checked-in configuration file to the action instead of inline JSON (spec: enterprise-hardening).
- Quoted/commented YAML parsing, ready-spec content checks, staged-spec validation, script/infrastructure coverage and enforcement of declared deterministic policy flags.

## 2026-05-13

Commits: `0a92a2d`, `035a861`, `5adbfbe`.

### Added

- Roles section in spec templates (`implementer`, `reviewer`, `qa`, `product_owner`) for per-spec responsibility assignment
- `roles.default_*` block in `.openspec/config.yaml` and `.openspec/defaults.yaml` for repo-wide default role assignments
- `scripts/openspec scaffold` now reads `roles.default_*` from config and pre-fills new specs
- Onboarding interview (`.openspec/onboarding.yaml`) prompts for default implementer / reviewer / qa / product_owner
- `Makefile` with convenience targets: `check`, `scaffold`, `scaffold-bug`, `test`, `status`, `setup`, `cleanup-template-specs`, `apply-branch-protection`
- `scripts/cleanup-template-specs` removes the template's internal design specs from a fresh fork
- `.vscode/settings.json` and `.vscode/extensions.json` with YAML schemas, markdownlint config, and recommended extensions
- `renovate.json.example` as an opt-in alternative to `dependabot.yml`
- Spec lifecycle state diagram in [`docs/OPENSPEC.md`](docs/OPENSPEC.md)
- **Enterprise hardening:**
  - `.github/workflows/license-scan.yml` + `.licenses/policy.yaml` — ScanCode-based OSS license enforcement
  - `.github/workflows/container-scan.yml` — Hadolint + Trivy scanning, auto-skips when no Dockerfile present
  - `.github/workflows/spec-metrics.yml` — weekly DORA-style report on spec status, role coverage, PR→spec link rate
  - `docs/branch-protection-ruleset.json` + `scripts/apply-branch-protection` — one-command branch protection bootstrap
  - `SECRETS.md` — secrets-management policy with rotation cadences and incident response
  - PR template extended with accessibility, privacy / data-handling, and security checklists
- `CONTRIBUTING.md` documents the `roles` block in the spec workflow
- `CLAUDE.md` Step 5 now instructs Claude to walk users through `roles` during scaffolding
- `CLAUDE.md` Step 6 now instructs Claude to clean up template-internal specs

## 2026-04-15

### Added

- Initial repository commit (`d07225a`). No tagged release date is recorded in the local Git history.

[Unreleased]: https://github.com/arananet/magnific_claude_code_plugin/commits/HEAD
