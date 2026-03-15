---
name: europe-developer-api
description: AI Engineer Europe 2026 developer endpoints, MCP server, and conference data APIs
---

# Europe Developer & AI Endpoints

AI Engineer Europe 2026 exposes several developer-friendly endpoints for building apps, AI integrations, and tools on top of conference data.

## Available Endpoints

All endpoints are relative to `https://ai.engineer`:

| Endpoint | Description |
|---|---|
| `/europe/llms.txt` | Basic conference info + schedule overview (plain text) |
| `/europe/llms-full.txt` | Full details: all talks, descriptions, and speakers (plain text) |
| `/europe/talks.json` | All talks/sessions as JSON (no sensitive data) |
| `/europe/speakers.json` | All speakers as JSON (no sensitive data) |
| `/europe/mcp` | MCP (Model Context Protocol) server endpoint |

## Quick Start

### Fetch data with curl

```bash
# Basic info
curl https://ai.engineer/europe/llms.txt

# Full details
curl https://ai.engineer/europe/llms-full.txt

# JSON endpoints
curl https://ai.engineer/europe/talks.json | jq .
curl https://ai.engineer/europe/speakers.json | jq .
```

### Use the npx CLI

```bash
# Show conference info
npx aieng europe

# List all speakers
npx aieng eu speakers

# List all talks
npx aieng eu talks

# Search for a speaker
npx aieng eu speakers --search "Matt"

# Filter talks by day
npx aieng eu talks --day "April 9"

# List all conferences
npx aieng --list
```

### MCP Integration

The MCP server at `/europe/mcp` implements the Model Context Protocol (JSON-RPC 2.0). You can use it with any MCP-compatible client.

**Available tools:**
- `get_conference_info` — Basic conference metadata
- `list_speakers` — All speakers (with optional search filter)
- `list_talks` — All talks (with optional day/type/track/search filters)
- `get_schedule` — Full schedule organized by day

**Example MCP request:**
```bash
curl -X POST https://ai.engineer/europe/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"list_speakers","arguments":{"search":"Anthropic"}}}'
```

**MCP client config (e.g. for Claude Desktop):**
```json
{
  "mcpServers": {
    "aie-europe": {
      "url": "https://ai.engineer/europe/mcp"
    }
  }
}
```

## Data Model

### Talks JSON structure
```json
{
  "conference": "AI Engineer Europe 2026",
  "dates": "April 8-10, 2026",
  "location": "London, UK",
  "totalTalks": 100,
  "talks": [
    {
      "title": "Talk Title",
      "description": "Talk description...",
      "day": "April 9",
      "time": "9:00-9:30am",
      "room": "Keynote",
      "type": "keynote",
      "track": "AI Agents",
      "speakers": ["Speaker Name"]
    }
  ]
}
```

### Speakers JSON structure
```json
{
  "conference": "AI Engineer Europe 2026",
  "totalSpeakers": 100,
  "speakers": [
    {
      "name": "Speaker Name",
      "role": "Role",
      "company": "Company",
      "twitter": "https://x.com/handle",
      "linkedin": "https://linkedin.com/in/...",
      "github": "https://github.com/...",
      "photoUrl": "https://ai.engineer/europe-speakers/photo.jpg",
      "talks": [...]
    }
  ]
}
```

## Sensitive Fields (stripped from public endpoints)

The following fields are NOT exposed in any public endpoint:
- `contact.email` — speaker email addresses
- `notes` — internal organizer notes
- `acceleventsSpeakerId` — internal Accelevents IDs
- `sessionId` — internal session IDs
- `invited` — whether speaker was invited vs CFP
- `cfpData` — call for papers submission details and review status

## Notes

- All endpoints return CORS headers (`Access-Control-Allow-Origin: *`)
- JSON endpoints support `OPTIONS` preflight requests
- Data is cached (`s-maxage=3600, stale-while-revalidate=86400`)
- Source code: [aiDotEngineer/aiecode2025](https://github.com/aiDotEngineer/aiecode2025)
