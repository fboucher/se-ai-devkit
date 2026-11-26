# Set up the Docs MCP server

The Docs MCP server gives your agent three read-only tools: `docs_search`, `docs_get_page`
and `docs_list`. It serves the public documentation only and needs no authentication. It is
**not** the authenticated BDP MCP server, which accesses live building data; you can use the
two side by side.

## Before you start

- Install [uv](https://docs.astral.sh/uv/getting-started/installation/). It provides `uvx`,
  which downloads and runs the server.
- Get the wheel URL: open the latest [release](../../../releases/latest) and copy the link of
  the attached `.whl` file. Use it in place of `<release-wheel-url>` below.

## How it runs

The server uses **stdio**: your agent starts it as a child process when it needs the tools
and talks to it through stdin/stdout. There is no port and **nothing to keep running**. You
only register the command; the agent starts and stops the server itself.

The docs it serves are the snapshot bundled in the wheel, as fresh as that release.

## Claude Code

Run this in your project:

```sh
claude mcp add --transport stdio se-devkit-docs -- uvx --from <release-wheel-url> devkit docs-mcp
```

Add `--scope user` to make it available in all your projects.

**Check it:** start `claude` and run `/mcp`. `se-devkit-docs` should show as connected with
3 tools.

## Claude Desktop

Add this to `claude_desktop_config.json` (Settings → Developer → Edit Config), then restart
the app:

```json
{
  "mcpServers": {
    "se-devkit-docs": {
      "command": "uvx",
      "args": ["--from", "<release-wheel-url>", "devkit", "docs-mcp"]
    }
  }
}
```

## VS Code / GitHub Copilot

Recent VS Code versions run Copilot chat on the **Copilot harness**, which reads MCP servers
from `.mcp.json` at the workspace root. Older versions read `.vscode/mcp.json`. Use the one
that matches your setup.

**Copilot harness:** add this to `.mcp.json` at the root of your workspace:

```json
{
  "mcpServers": {
    "se-devkit-docs": {
      "type": "local",
      "command": "uvx",
      "args": ["--from", "<release-wheel-url>", "devkit", "docs-mcp"],
      "tools": ["*"]
    }
  }
}
```

**Older VS Code setup:** add this to `.vscode/mcp.json`, then click **Start** above the
server entry:

```json
{
  "servers": {
    "se-devkit-docs": {
      "type": "stdio",
      "command": "uvx",
      "args": ["--from", "<release-wheel-url>", "devkit", "docs-mcp"]
    }
  }
}
```

**Check it:** open a **new** Copilot chat session in Agent mode, select the tools icon and
look for the three `docs_*` tools.

## GitHub Copilot CLI

Add the same `se-devkit-docs` entry as for the Copilot harness to `~/.copilot/mcp-config.json`
(or `$COPILOT_HOME/mcp-config.json`), under `mcpServers`.

## Cursor

Add this to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "se-devkit-docs": {
      "command": "uvx",
      "args": ["--from", "<release-wheel-url>", "devkit", "docs-mcp"]
    }
  }
}
```

## Try it

Ask your agent, for example:

- *"Use docs_list to show me the documentation sections."*
- *"Search the docs for how to authenticate to the GraphQL API, then open the best page."*
- *"Search only the REST API section for historical values."*

## Use another docs folder

By default the server uses its bundled snapshot. To serve another docs checkout, add
`--docs <path>` after `docs-mcp`, or set the `SE_DEVKIT_DOCS` environment variable. Use an
absolute path: the agent may start the server from another folder.

## Troubleshooting

| Symptom | Fix |
|---|---|
| VS Code says *"This server needs to be migrated manually"* or *"Compatibility with Copilot could not be determined"* | Your server is in `.vscode/mcp.json` but Copilot now reads `.mcp.json`. Add the Copilot harness entry above, or run **Chat: Open Customizations** → **Migrations**. See [Migrate customizations](https://code.visualstudio.com/docs/agent-customization/migrate-customizations). |
| VS Code says *"This server is not associated with the current workspace"* | Open the folder that holds the config file itself (**File → Open Folder**), not a parent folder or a single file. |
| The tools don't appear after a config change | Start a new chat session, or reload the window (**Developer: Reload Window**). |
| `uvx` is not found | Install uv, then restart your editor or agent so it sees the new `PATH`. |
| uv fails with certificate errors on a corporate network | Set `UV_SYSTEM_CERTS=1` so uv trusts the system certificate store. |
