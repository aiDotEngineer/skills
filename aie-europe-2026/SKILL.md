---
name: aie-europe-2026
description: >
  Query AI Engineer Europe 2026 conference data — speakers, talks, schedule, and more.
  Use when building apps, AI integrations, or tools on top of conference data. Provides
  REST endpoints (JSON + plain text), an MCP server for agent tool calls, and a CLI.
  Covers 150+ talks, 150+ speakers, workshops, and the full 3-day schedule.
license: MIT
compatibility: Requires network access to https://ai.engineer
metadata:
  author: aidotengineer
  version: "1.0"
  conference-dates: "April 8-10, 2026"
  conference-location: "London, UK"
  conference-venue: "Park Plaza Westminster Bridge"
---

# AI Engineer Europe 2026

Conference data APIs, MCP server, and CLI for AI Engineer Europe 2026 (April 8-10, London).

## When to use this skill

- Building apps or dashboards with conference data
- Querying speakers, talks, or schedule programmatically
- Connecting an AI agent to the conference MCP server
- Generating conference summaries, recommendations, or search features
- Looking up who's speaking, what talks are on which day/track, or session details

## Endpoints

Base URL: `https://ai.engineer`

| Endpoint | Format | Description |
|---|---|---|
| `/europe/llms.txt` | Plain text | Conference overview optimized for LLM consumption |
| `/europe/llms-full.txt` | Plain text | Full details — every talk, speaker bio, schedule |
| `/europe/talks.json` | JSON | All talks with titles, descriptions, speakers, times, rooms, tracks |
| `/europe/speakers.json` | JSON | All speakers with roles, companies, social links, photos, talks |
| `/europe/mcp` | JSON-RPC | MCP server — tool calls for querying conference data |

All endpoints are public, free, and CORS-enabled. Data is cached (`s-maxage=3600, stale-while-revalidate=86400`).

## Quick start

### curl

```bash
# Plain text overview (good for piping to an LLM)
curl https://ai.engineer/europe/llms.txt

# Full conference dump
curl https://ai.engineer/europe/llms-full.txt

# Structured JSON
curl https://ai.engineer/europe/talks.json | jq '.talks[:3]'
curl https://ai.engineer/europe/speakers.json | jq '.speakers[:3]'
```

### CLI (`@aidotengineer/aie`)

No install needed — runs via npx:

```bash
npx @aidotengineer/aie --list              # List all conferences
npx @aidotengineer/aie europe              # Europe conference info
npx @aidotengineer/aie eu speakers         # All speakers
npx @aidotengineer/aie eu speakers --search "Anthropic"
npx @aidotengineer/aie eu talks --day "April 9"
npx @aidotengineer/aie eu talks --type workshop
npx @aidotengineer/aie eu search "agents"  # Full-text search
npx @aidotengineer/aie eu speakers --json  # Raw JSON output
npx @aidotengineer/aie eu mcp             # MCP connection info
```

### JavaScript / TypeScript

```typescript
const res = await fetch('https://ai.engineer/europe/speakers.json');
const { speakers, totalSpeakers } = await res.json();

// Find speakers from Anthropic
const anthropic = speakers.filter(s =>
  s.company?.toLowerCase().includes('anthropic')
);
console.log(`${anthropic.length} speakers from Anthropic`);

// Get all keynotes
const talks = await fetch('https://ai.engineer/europe/talks.json').then(r => r.json());
const keynotes = talks.talks.filter(t => t.type === 'keynote');
console.log(keynotes.map(k => `${k.time}: ${k.title} — ${k.speakers.join(', ')}`));
```

### Python

```python
import requests

# --- Fetch and explore talks ---
data = requests.get('https://ai.engineer/europe/talks.json').json()
print(f"{data['totalTalks']} talks across {data['dates']}")

# Day 2 talks
day2 = [t for t in data['talks'] if t.get('day') == 'April 9']
for talk in day2:
    speakers = ', '.join(talk.get('speakers', []))
    print(f"{talk.get('time', '?')}: {talk.get('title', 'TBA')} — {speakers}")

# Talks about agents
agent_talks = [t for t in data['talks']
               if 'agent' in (t.get('title') or '').lower()
               or t.get('track', '').lower() == 'ai agents']
print(f"\n{len(agent_talks)} talks about agents")

# --- Fetch speakers ---
sp = requests.get('https://ai.engineer/europe/speakers.json').json()

# Speakers with GitHub profiles
with_github = [s for s in sp['speakers'] if s.get('github')]
print(f"\n{len(with_github)} speakers with GitHub profiles")
for s in with_github[:5]:
    print(f"  {s['name']} ({s.get('company', '?')}): {s['github']}")

# Group speakers by company
from collections import Counter
companies = Counter(s.get('company') for s in sp['speakers'] if s.get('company'))
for company, count in companies.most_common(10):
    print(f"  {company}: {count} speakers")
```

### Python — MCP tool call

```python
import requests
import json

MCP_URL = 'https://ai.engineer/europe/mcp'

def mcp_call(tool_name: str, arguments: dict = {}) -> dict:
    """Call an MCP tool and return the parsed result."""
    resp = requests.post(MCP_URL, json={
        'jsonrpc': '2.0',
        'id': 1,
        'method': 'tools/call',
        'params': {'name': tool_name, 'arguments': arguments}
    }, headers={'Content-Type': 'application/json', 'Accept': 'application/json'})
    result = resp.json()['result']['content'][0]['text']
    return json.loads(result)

# Get conference info
info = mcp_call('get_conference_info')
print(f"{info['name']} — {info['dates']} — {info['location']}")

# Search speakers
speakers = mcp_call('list_speakers', {'search': 'Google'})
for s in speakers['speakers']:
    print(f"  {s['name']}: {s.get('role', '')} @ {s.get('company', '')}")

# Get Day 2 keynotes
keynotes = mcp_call('list_talks', {'day': 'April 9', 'type': 'keynote'})
for t in keynotes['talks']:
    print(f"  {t['time']}: {t['title']} — {', '.join(t['speakers'])}")

# Get schedule for one day
schedule = mcp_call('get_schedule', {'day': 'April 10'})
for session in schedule['days'][0]['sessions']:
    print(f"  {session.get('time', '?')}: {session.get('title', 'TBA')}")
```

## MCP server

The MCP server at `https://ai.engineer/europe/mcp` implements JSON-RPC 2.0 over Streamable HTTP.

### Client config

Add to your Claude Desktop, Cursor, Windsurf, or any MCP client config:

```json
{
  "mcpServers": {
    "aie-europe": {
      "url": "https://ai.engineer/europe/mcp"
    }
  }
}
```

### Available tools

| Tool | Description | Optional params |
|---|---|---|
| `get_conference_info` | Dates, venue, links, metadata | — |
| `list_speakers` | Speakers with roles, companies, socials, talks | `search` |
| `list_talks` | Talks with descriptions, times, rooms, tracks | `day`, `type`, `track`, `search` |
| `get_schedule` | Full schedule organized by day | `day` |

### Example tool call (curl)

```bash
curl -X POST https://ai.engineer/europe/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "list_speakers",
      "arguments": { "search": "Anthropic" }
    }
  }'
```

### Example tool call (Python)

```python
import requests, json

resp = requests.post('https://ai.engineer/europe/mcp', json={
    'jsonrpc': '2.0', 'id': 1,
    'method': 'tools/call',
    'params': {'name': 'list_talks', 'arguments': {'track': 'MCP'}}
}, headers={'Content-Type': 'application/json', 'Accept': 'application/json'})

result = json.loads(resp.json()['result']['content'][0]['text'])
for talk in result['talks']:
    print(f"{talk['title']} — {', '.join(talk['speakers'])}")
```

### Initialize + discover tools

```bash
# Initialize session
curl -X POST https://ai.engineer/europe/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"my-client","version":"1.0.0"}}}'

# List tools
curl -X POST https://ai.engineer/europe/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list"}'

# GET also returns server info + tool definitions
curl https://ai.engineer/europe/mcp | jq .
```

See `references/MCP.md` for full tool schemas and response formats.

## Data model

### Talk

```typescript
type PublicTalk = {
  title?: string;
  description?: string;
  day?: string;        // "April 8" | "April 9" | "April 10"
  time?: string;       // "9:00-9:30am"
  room?: string;       // "Keynote" | "Abbey" | "Fleming" | "Moore" | "St. James" | "Westminster"
  type?: string;       // "keynote" | "talk" | "workshop" | "panel" | "break"
  track?: string;      // "AI Agents" | "Coding Agents" | "MCP" | "Open Source" | "GPUs & LLM Infrastructure" | ...
  speakers: string[];
};
```

### Speaker

```typescript
type PublicSpeaker = {
  name: string;
  role?: string;
  company?: string;
  companyDescription?: string;
  twitter?: string;    // Full URL: "https://x.com/handle"
  linkedin?: string;   // Full URL
  github?: string;     // Full URL
  website?: string;
  photoUrl?: string;   // "https://ai.engineer/europe-speakers/name.jpg"
  talks: PublicTalk[];
};
```

See `references/SCHEMAS.md` for full response envelope structures and real API response examples.

## Edge cases

- Some talks have empty `description` — fall back to title + speakers
- `speakers` array can be empty for break/logistics sessions
- `type` field may be missing for some sessions — treat as "talk"
- Speaker photos are served from `ai.engineer/europe-speakers/` — some speakers may not have a photo
- Social links (twitter, linkedin, github) are full URLs when present, `undefined` when absent
- The `track` field only exists on Day 2-3 multi-track sessions; Day 1 workshops don't have tracks

## Sensitive fields (never exposed)

These fields exist in the source data but are stripped from all public endpoints:

- `contact.email` — speaker email addresses
- `notes` — internal organizer notes
- `acceleventsSpeakerId` — internal Accelevents IDs
- `sessionId` — internal session identifiers
- `invited` — whether speaker was invited vs CFP
- `cfpData` — call for papers submissions and review status

## Links

- Website: [ai.engineer/europe](https://ai.engineer/europe)
- Source code: [github.com/aiDotEngineer/aiecode2025](https://github.com/aiDotEngineer/aiecode2025)
- CLI on npm: [@aidotengineer/aie](https://www.npmjs.com/package/@aidotengineer/aie)
- Twitter: [@aiDotEngineer](https://x.com/aiDotEngineer)
