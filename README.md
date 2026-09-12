# AI Engineer Skills

The canonical agent interface is **[AI Engineer MCP](https://ai.engineer/data#mcp)** at `https://ai.engineer/mcp`.

Use MCP to discover conferences, schedules, talks and transcript passages, and to apply privately to attend AIE CODE 2026. Read [llms.txt](https://ai.engineer/llms.txt) for live instructions and REST endpoints, or the [data guide](https://ai.engineer/data.md) for schemas. Applicant records and scores are never public.

This repository remains available for skill users. It is a thin discovery guide; live MCP schemas and documentation are authoritative. No separate conference data or MCP implementation is maintained here.

## Available skills

- **ai-engineer** — conference and talk discovery, plus private CODE 2026 attendee applications.
- **aie-europe-2026** — existing install name preserved; now directs agents to the canonical MCP, current Europe data and CODE 2026 attendee application guidance.
- **schedule-design** — guidance for designing conference schedules; independent of MCP connectivity.

```bash
npx skills add aidotengineer/skills --skill ai-engineer
```

To apply through an agent, read requirements, validate answers, review the complete application and approve submission. Attendee applications are for CODE 2026, not NYC or speaker proposals. CODE speaker proposals use [Sessionize](https://sessionize.com/aiecode26/).

MIT
