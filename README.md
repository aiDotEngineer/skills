# AI Engineer Skills

A collection of agent skills for [AI Engineer](https://ai.engineer) conference data and developer APIs.

Skills follow the [Agent Skills](https://skills.sh) format and can be installed with a single command.

## Available Skills

### europe-developer-api

Access AI Engineer Europe 2026 conference data through REST endpoints, JSON APIs, an MCP server, and a CLI tool.

**Use when:**
- Building apps or integrations on top of conference data
- Querying speaker or talk information programmatically
- Connecting an AI agent to the conference MCP server
- Looking up schedule, speaker, or session details

**Endpoints:**
- `/europe/llms.txt` — Plain text conference overview
- `/europe/llms-full.txt` — Full details with all talks and speakers
- `/europe/talks.json` — All talks as JSON
- `/europe/speakers.json` — All speakers as JSON
- `/europe/mcp` — MCP server (Model Context Protocol)

## Installation

```bash
npx skills add aidotengineer/skills
```

Or install a specific skill:

```bash
npx skills add aidotengineer/skills --skill europe-developer-api
```

## License

MIT
