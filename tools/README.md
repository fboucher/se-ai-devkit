# tools

Python tooling that checks `docs/` and builds the kit's outputs from it.

| Command | What it does |
|---|---|
| `devkit validate` | Checks front matter and links of every page under `docs/` |
| `devkit llms` | Generates `public/llms.txt`, `public/llms-full.txt` and `public/llms-full/<section>.txt` (settings: `tools/llms.yml`) |
| `devkit llms --check` | Fails if `public/` is out of date (used in CI) |
| `devkit skill` | Generates the Agent Skill / Claude Code plugin in `plugins/` (settings: `tools/skill.yml`) |
| `devkit skill --check` | Fails if `plugins/` is out of date (used in CI) |
| `devkit skill --zip <path>` | Writes the skill folder as a zip (used by the release workflow) |
| `devkit docs-mcp [--docs PATH]` | Serves `docs_search`, `docs_get_page` and `docs_list` over stdio |

Run from the **repository root**:

```bash
uv run --project tools devkit validate
uv run --project tools devkit llms
uv run --project tools devkit skill
uv run --project tools devkit docs-mcp --docs docs
uv run --project tools pytest tools
uv run --project tools ruff check tools
```

`docs/api/` is not produced here: it is written by the exporter maintained in the internal
docs repo, which calls `devkit validate` and `devkit llms` in a local clone of this repo.
The Docs MCP server is a separate, public documentation interface; unlike the authenticated
BDP MCP server, it does not connect to live building data. Its default docs are the snapshot
bundled with the installed wheel; `--docs` or `SE_DEVKIT_DOCS` selects another docs tree.

## Test the Docs MCP server from a checkout

The server uses stdio, so you don't keep it running: register the command in your agent
and the agent starts it. Use absolute paths, because the agent may start it from another
folder. For example, in Claude Code:

```sh
claude mcp add --transport stdio se-devkit-docs -- uv run --project <repo>/tools devkit docs-mcp --docs <repo>/docs
```

For other agents, use the same command and arguments in the configs from
[setup/docs-mcp-server.md](../setup/docs-mcp-server.md), with `uv` as the command.
