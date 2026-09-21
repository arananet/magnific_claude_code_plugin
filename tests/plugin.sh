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
for json in .claude-plugin/plugin.json .claude-plugin/marketplace.json .mcp.json hooks/hooks.json; do
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
md_files=(commands/*.md skills/*/SKILL.md agents/*.md)
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

# The manifest schema takes arrays for these, not directory strings — a string
# fails installation with "agents: Invalid input". They are also unnecessary:
# commands/, agents/ and skills/ at the plugin root are auto-discovered.
python3 - <<'PYSCHEMA' || failures=$((failures + 1))
import json, sys
from pathlib import Path
m = json.load(open('.claude-plugin/plugin.json'))
for field in ('commands', 'agents', 'skills'):
    if field in m and not isinstance(m[field], list):
        print(f"FAIL: plugin.json {field!r} is {type(m[field]).__name__}, not a list — "
              "installation rejects a directory string here", file=sys.stderr)
        sys.exit(1)
for d in ('commands', 'agents', 'skills'):
    if d not in m and not Path(d).is_dir():
        print(f"FAIL: {d}/ is missing and not declared in the manifest, so nothing loads it",
              file=sys.stderr)
        sys.exit(1)
print('ok: manifest component fields are schema-valid; auto-discovered dirs exist')
PYSCHEMA

# --- the repo is a usable marketplace -----------------------------------------
# Without .claude-plugin/marketplace.json, `/plugin marketplace add <repo>` fails
# with "Marketplace not found" and the plugin cannot be installed at all.
python3 - <<'PYMKT' || failures=$((failures + 1))
import json, sys
from pathlib import Path
try:
    mkt = json.load(open('.claude-plugin/marketplace.json'))
except FileNotFoundError:
    print("FAIL: .claude-plugin/marketplace.json is missing — the repo is not installable",
          file=sys.stderr)
    sys.exit(1)
if not mkt.get('name'):
    print("FAIL: marketplace.json has no name", file=sys.stderr)
    sys.exit(1)
plugins = mkt.get('plugins') or []
if not plugins:
    print("FAIL: marketplace.json lists no plugins", file=sys.stderr)
    sys.exit(1)
manifest_name = json.load(open('.claude-plugin/plugin.json'))['name']
names = [p.get('name') for p in plugins]
if manifest_name not in names:
    print(f"FAIL: marketplace lists {names}, but plugin.json is named {manifest_name!r}",
          file=sys.stderr)
    sys.exit(1)
for p in plugins:
    src = p.get('source')
    if not src:
        print(f"FAIL: plugin {p.get('name')!r} has no source", file=sys.stderr)
        sys.exit(1)
    if isinstance(src, str) and (src.startswith('./') or src == '.'):
        if not (Path(src) / '.claude-plugin' / 'plugin.json').is_file():
            print(f"FAIL: source {src!r} has no .claude-plugin/plugin.json", file=sys.stderr)
            sys.exit(1)
print(f"ok: installable as {manifest_name}@{mkt['name']} "
      f"(/plugin marketplace add, then /plugin install)")
PYMKT

# The wrong install form cost a real user a failed install; keep the right one
# in the docs.
for doc in README.md commands/setup.md; do
  if grep -q 'plugin marketplace add arananet/magnific_claude_code_plugin' "$doc" \
     && grep -q 'plugin install magnific@arananet' "$doc"; then
    pass "$doc documents the two-step install"
  else
    fail "$doc does not document '/plugin marketplace add' + '/plugin install magnific@arananet'"
  fi
done

# The README deliberately does not hand out the bare `claude mcp add` line: it
# is the path that skips the guard, the ledger, the commands and the agent.
for doc in README.md commands/*.md; do
  if grep -q 'claude mcp add' "$doc"; then
    fail "$doc reintroduces the bare 'claude mcp add' install, bypassing the plugin"
  fi
done
pass "docs do not hand out the bare MCP-add install"

# --- hooks are wired to scripts that exist and behave -------------------------
python3 - <<'PYHOOK' || failures=$((failures + 1))
import json, re, sys
# hooks/hooks.json is the auto-discovered location. A session reporting
# "0 hooks" means none of this loaded, so the path matters more than it looks.
cfg = json.load(open('hooks/hooks.json'))['hooks']
# The MCP server is namespaced when it comes from a plugin — the session shows
# it as plugin:magnific:magnific — so a matcher anchored on mcp__magnific__
# never fires.
namespaced = "mcp__plugin:magnific:magnific__images_generate"
for event in ('PreToolUse', 'PostToolUse'):
    entries = cfg.get(event) or []
    if not entries:
        print(f"FAIL: hooks.json defines no {event} hook", file=sys.stderr)
        sys.exit(1)
    for entry in entries:
        matcher = entry.get('matcher', '')
        if not re.search(matcher, namespaced):
            print(f"FAIL: {event} matcher {matcher!r} does not match a namespaced "
                  f"plugin tool name like {namespaced!r}", file=sys.stderr)
            sys.exit(1)
        if re.search(matcher, "Bash") or re.search(matcher, "mcp__github__get_me"):
            print(f"FAIL: {event} matcher {matcher!r} is too broad", file=sys.stderr)
            sys.exit(1)
print('ok: hooks.json wires both events, matching namespaced magnific tools only')
PYHOOK

for script in scripts/magnific/guard.py scripts/magnific/capture.py scripts/magnific/report.py; do
  if [[ ! -f $script ]]; then
    fail "$script is missing"
  elif python3 -c "import ast,sys; ast.parse(open(sys.argv[1]).read())" "$script"; then
    pass "$script parses"
  else
    fail "$script has a syntax error"
  fi
done

# A hook that crashes breaks the user's tool call, so both must exit 0 on junk.
for hook in scripts/magnific/guard.py scripts/magnific/capture.py; do
  if printf 'not json' | python3 "$hook" >/dev/null 2>&1; then
    pass "$(basename "$hook") survives malformed input"
  else
    fail "$(basename "$hook") exits non-zero on malformed input"
  fi
done

# --- the advertised commands exist --------------------------------------------
for cmd in setup upscale generate creations library budget batch brief doctor; do
  [[ -f "commands/$cmd.md" ]] && pass "/magnific:$cmd present" || fail "commands/$cmd.md is missing"
done

# --- hook logic unit tests -----------------------------------------------------
if python3 tests/magnific_hooks_test.py >/dev/null 2>&1; then
  pass "hook unit tests (tests/magnific_hooks_test.py)"
else
  fail "hook unit tests failed — run: python3 tests/magnific_hooks_test.py"
fi

if (( failures )); then

  printf '\n%d check(s) failed\n' "$failures" >&2
  exit 1
fi
printf '\nAll plugin checks passed\n'
