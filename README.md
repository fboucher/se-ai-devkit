# Schneider Electric (SE) AI Developer Kit

Everything your AI coding agent (Claude Code, GitHub Copilot, Cursor, Codex and others)
needs to write working code against the **Schneider Electric EcoStruxure™ Building Data
Platform APIs**: REST API, GraphQL API and Event Hubs.

> [!NOTE]
> **Early access.** This kit is shared with selected partners while it is being built.
> Feedback is welcome.

## What's in the kit

| | Tool | What it gives your agent | Status |
|---|---|---|---|
| 📄 | [**Agent-friendly docs**](#-agent-friendly-docs) | The official API documentation as clean markdown, one page per topic | ✅ Ready |
| 🔗 | [**llms.txt**](#-llmstxt) | One URL that indexes every page, plus full-text bundles | ✅ Ready |
| 🧩 | [**Agent Skill**](#-agent-skill) | All the docs plus a search tool, installed once and loaded only when needed | ✅ Ready |
| 🔍 | [**Docs MCP server**](#-docs-mcp-server) | Search and fetch docs pages as tools in your agent | ✅ Ready |
| 🏢 | [**Brick schema guidance**](#-brick-schema-guidance) | How our APIs use the Brick ontology, with worked examples | 🚧 Coming soon |

**Which one should I use?**

- **Quickest start, any agent:** paste the [llms.txt](#-llmstxt) URL into your prompt.
- **Working with the APIs every day:** install the [Agent Skill](#-agent-skill). Your agent
  looks up the right page by itself, offline.
- **Building your own tooling or reading the docs yourself:** use the
  [agent-friendly docs](#-agent-friendly-docs) directly.

All tools are generated from the same pages, so they always say the same thing. Setup steps for each tool are in [`setup/`](setup/).

---

## 📄 Agent-friendly docs

The official Building Data Platform documentation, converted to plain markdown that agents read well: one page per topic, a short description on every page, no site navigation, and screenshots replaced by text. Pages for deprecated features are clearly labelled.

| Folder | Contents |
|---|---|
| [`docs/api/`](docs/api/) | Concepts, REST API, GraphQL API, implementation guides, FAQ, release notes |
| [`docs/guides/`](docs/guides/) | Task-oriented walkthroughs |

The pages are regenerated from the official product documentation on each docs release.

## 🔗 llms.txt

A single index, following the [llms.txt](https://llmstxt.org) convention, that any agent can fetch:

```text
https://schneiderelectricbuildings.github.io/se-ai-devkit/llms.txt
```

It links every page, plus full-text bundles: all pages in one file, or one file per section for agents with a small context window.

**Set it up:** [setup/llms-txt.md](setup/llms-txt.md)

## 🧩 Agent Skill

An [Agent Skill](https://agentskills.io) named `building-data-platform-api`. It bundles every page, an index, rules for using the docs (look up the page first, use documented names only, authenticate, test against UAT) and a search script. Your agent loads it only when a task involves these APIs, and finds the right page without reading everything. Works with Claude Code, GitHub Copilot, Cursor, OpenAI Codex and claude.ai.

**Set it up:** [setup/agent-skill.md](setup/agent-skill.md)

## 🔍 Docs MCP server

A public, read-only [MCP](https://modelcontextprotocol.io) server that lets your agent search and browse the docs using `docs_search`, `docs_get_page` and `docs_list`. It runs locally over stdio, needs no authentication, and serves the docs snapshot of the release you install. Works with Claude Code, Claude Desktop, VS Code / GitHub Copilot, Copilot CLI and Cursor.

The Docs MCP server only serves public documentation. It is **not** the separate, authenticated BDP MCP server, which accesses live building data; the two can be used side by side.

**Set it up:** [setup/docs-mcp-server.md](setup/docs-mcp-server.md)

## 🏢 Brick schema guidance

> 🚧 **Coming soon.**

Our APIs describe buildings with the [Brick schema](https://brickschema.org), an open ontology for building data. This guidance will cover which Brick version our APIs target, the classes and relationships they return, our conventions, and worked examples such as *"find all temperature sensors feeding a given air handling unit"*. It links to the official Brick definitions rather than copying them.

---

## Good to know

- **Documentation only.** The kit contains no live data and no credentials. Calling the APIs requires authentication, described in the *Authentication* pages.
- **Test against UAT.** The API introduction pages document the UAT environment partners and ISVs use for testing.
- **Examples use fictional identifiers.** Replace them with IDs from your own environment.
- Live building data is only available through the authenticated APIs (or the separate, authenticated API MCP server), never through this kit.

## Support

**For issues with examples or documentation:**
Please [open a GitHub issue](https://github.com/fboucher/se-ai-devkit/issues) with a clear description of the problem, including any error messages or examples of what's unclear.

## Contributing and license

See [CONTRIBUTING.md](CONTRIBUTING.md). The examples and documentation in this starter pack are released under the [MIT License](LICENSE), so you are free to use, copy, and modify them in your own projects, including commercial ones.