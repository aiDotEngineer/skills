# AI Engineer Skills

Agent skills for [AI Engineer](https://ai.engineer) conference data and developer APIs.

Skills follow the [Agent Skills](https://agentskills.io/specification) format and work with 40+ agents including Devin, Claude Code, Cursor, Windsurf, and Codex.

## Available Skills

### aie-europe-2026

Query AI Engineer Europe 2026 conference data — speakers, talks, schedule, and more. Provides REST endpoints (JSON + plain text), an MCP server for agent tool calls, and a CLI.

**Includes:**
- 5 public endpoints (JSON, plain text, MCP)
- TypeScript type definitions for all data models
- Real API response examples from live production data
- MCP server tool schemas and JSON-RPC examples
- CLI commands via `@aidotengineer/aie`
- Helper scripts for common tasks
- Edge case documentation

### public-qa-chatbot

Best practices for building an unauthenticated public Q&A chatbot widget. Covers rate limiting, security hardening, cost optimization, semantic caching, observability, UX patterns, and architecture. Tech-agnostic with swappable alternatives for each component (LLM provider, hosting, rate limiter, vector DB, observability).

**Includes:**
- Multi-layer rate limiting patterns (per-turn, per-visitor, global)
- Security hardening checklist (origin validation, input limits, safe errors)
- Semantic caching with vector similarity search
- Observability/tracing integration patterns
- UX patterns (markdown, draggable/resizable, FAQ list, hover previews)
- Swappable tech alternatives table for every component
- Production implementation checklist

## Installation

```bash
npx skills add aidotengineer/skills
```

Or install a specific skill:

```bash
npx skills add aidotengineer/skills --skill aie-europe-2026
```

## Links

- [AI Engineer Europe 2026](https://ai.engineer/europe)
- [Developer & AI page](https://ai.engineer/europe/developers)
- [Agent Skills spec](https://agentskills.io/specification)
- [skills.sh](https://skills.sh)

## License

MIT
