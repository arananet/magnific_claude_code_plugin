#!/usr/bin/env bash
# Contract tests for the Magnific Claude Code plugin.
# Bash + python3 only; no network, no Magnific account required.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

failures=0
fail() { printf 'FAIL: %s\n' "$*" >&2; failures=$((failures + 1)); }
pass() { printf 'ok: %s\n' "$*"; }

# --- every plugin JSON file parses -------------------------------------------
for json in .claude-plugin/plugin.json .mcp.json; do
  [[ -f $json ]] || { fail "$json is missing"; continue; }
  if python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$json" 2>/dev/null; then
    pass "$json parses"
  else
    fail "$json is not valid JSON"
  fi
done

# --- manifest carries the required fields ------------------------------------
python3 - <<'PY' || failures=$((failures + 1))
import json, sys
m = json.load(open('.claude-plugin/plugin.json'))
missing = [f for f in ('name', 'description', 'version', 'author') if not m.get(f)]
if missing:
    print(f"FAIL: plugin.json missing required field(s): {', '.join(missing)}", file=sys.stderr)
    sys.exit(1)
if m['name'] != 'magnific':
    print(f"FAIL: plugin name is {m['name']!r}, expected 'magnific'", file=sys.stderr)
    sys.exit(1)
print('ok: plugin.json has name, description, version, author')
PY

# --- the MCP server is the OAuth HTTP endpoint, with no key plumbed in --------
python3 - <<'PY' || failures=$((failures + 1))
import json, re, sys
cfg = json.load(open('.mcp.json'))
srv = cfg.get('mcpServers', {}).get('magnific')
if srv is None:
    print("FAIL: .mcp.json defines no 'magnific' server", file=sys.stderr)
    sys.exit(1)
if srv.get('type') != 'http':
    print(f"FAIL: magnific transport is {srv.get('type')!r}, expected 'http'", file=sys.stderr)
    sys.exit(1)
if srv.get('url') != 'https://mcp.magnific.com':
    print(f"FAIL: magnific url is {srv.get('url')!r}, expected https://mcp.magnific.com", file=sys.stderr)
    sys.exit(1)
# Auth is browser OAuth. A key or token in this file would be both wrong and a leak.
blob = json.dumps(cfg)
if re.search(r'(?i)(api[_-]?key|secret|token|authorization|bearer)', blob):
    print("FAIL: .mcp.json references a key/token — the endpoint is OAuth-only", file=sys.stderr)
    sys.exit(1)
print('ok: magnific registered as https://mcp.magnific.com over OAuth, no credentials in config')
PY

# --- commands and skills have usable frontmatter ------------------------------
shopt -s nullglob
md_files=(commands/*.md skills/*/SKILL.md)
(( ${#md_files[@]} )) || fail "no command or skill files found"
for md in "${md_files[@]}"; do
  if [[ $(head -1 "$md") != '---' ]]; then
    fail "$md does not open with YAML frontmatter"
    continue
  fi
  # frontmatter is everything up to the second '---'
  if awk 'NR>1 && /^---$/{exit} NR>1' "$md" | grep -q '^description:[[:space:]]*[^[:space:]]'; then
    pass "$md has a description"
  else
    fail "$md frontmatter has no non-empty description"
  fi
done

# --- the four advertised commands exist ---------------------------------------
for cmd in setup upscale generate creations; do
  [[ -f "commands/$cmd.md" ]] && pass "/magnific:$cmd present" || fail "commands/$cmd.md is missing"
done

if (( failures )); then
  printf '\n%d check(s) failed\n' "$failures" >&2
  exit 1
fi
printf '\nAll plugin checks passed\n'
