---
description: Connect the Magnific MCP server and sign in (OAuth — no API key needed)
---

Get the user connected to Magnific.

1. Check whether the `magnific` MCP server is already connected in this session.
   If the plugin is installed, it is registered automatically from the plugin's
   `.mcp.json` and nothing needs adding.
2. If it is not present, work out which case it is:

   - **The plugin was never installed.** It installs from this repo as a
     marketplace, in two steps:

     ```bash
     /plugin marketplace add arananet/magnific_claude_code_plugin
     /plugin install magnific@arananet
     ```

     `/plugin install arananet/magnific_claude_code_plugin` fails with
     `Marketplace ... not found` — `/plugin install` takes `plugin@marketplace`,
     not a repo path.

   - **They only want the server**, without the hooks, commands, agent or skill:

     ```bash
     claude mcp add --transport http magnific https://mcp.magnific.com
     ```

   Either way, restart Claude Code afterwards.
3. Explain the auth model in one or two lines: **Magnific's MCP endpoint uses
   browser OAuth, not an API key.** The first tool call opens a Magnific sign-in
   in the browser; approving it stores the session in the client. There is nothing
   to paste, and no key should ever be added to `.mcp.json` or the environment.
   (Magnific's REST API does use API keys — that is a different surface.)
4. If the server is connected, list the tools it advertises so the user sees what
   their account can actually do, and mention that generations spend Magnific credits.

Do not run a paid generation as a connection test.
