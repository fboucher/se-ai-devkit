# Set up the Agent Skill

The skill is named `building-data-platform-api`.

## Claude Code

Requires Claude Code 2.1.275 or later.

```text
/plugin install se-ai-devkit --marketplace SchneiderElectricBuildings/se-ai-devkit
```

Or in two steps: `/plugin marketplace add SchneiderElectricBuildings/se-ai-devkit`, then
`/plugin install se-ai-devkit@se-ai-devkit`.

**Updates:** get new docs with `claude plugin update se-ai-devkit`, or turn on auto-update
for this marketplace under `/plugin` → Marketplaces (it is off by default).

## GitHub Copilot, Cursor, OpenAI Codex

Download `building-data-platform-api.zip` from the latest [release](../../../releases/latest)
and unzip it into `.agents/skills/` in your project (or `~/.agents/skills/` for all your
projects).

## claude.ai

Upload the same zip as a skill in your settings.
