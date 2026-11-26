# Set up llms.txt

The index, following the [llms.txt](https://llmstxt.org) convention, is published at:

```text
https://schneiderelectricbuildings.github.io/se-ai-devkit/llms.txt
```

## Point your agent at it

| Agent | How |
|---|---|
| Any agent | Start your prompt with: *"Read `<url>/llms.txt` and the pages it links to before writing code against the Building Data Platform APIs."* |
| Claude Code | Add that sentence to your project's `CLAUDE.md` |
| Cursor | Add the URL as a custom doc (`@Docs` → *Add new doc*), then mention it with `@` |
| GitHub Copilot | Add that sentence to `.github/copilot-instructions.md` |

## Full-text bundles

Need everything at once? `llms-full.txt` holds every page in one file, and
`llms-full/<section>.txt` (for example `llms-full/rest-api.txt`) holds one section, for agents
with a small context window. `llms.txt` links them all under **Full text**.
