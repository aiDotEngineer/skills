# MCP Server Reference

Complete reference for the AI Engineer Europe 2026 MCP server.

**Endpoint:** `https://ai.engineer/europe/mcp`
**Protocol:** JSON-RPC 2.0 over Streamable HTTP
**Spec version:** `2025-03-26`

## Server info

```json
{
  "name": "aie-europe-2026",
  "version": "1.0.0",
  "protocolVersion": "2025-03-26",
  "capabilities": { "tools": {} }
}
```

## Transport

- `POST` — JSON-RPC requests (single or batch)
- `GET` — Returns server info + tool definitions (no JSON-RPC needed)
- `OPTIONS` — CORS preflight

## Tool definitions

### get_conference_info

Returns conference metadata: name, dates, location, venue, website, ticket URL, social links.

```json
{
  "name": "get_conference_info",
  "description": "Get basic information about AI Engineer Europe 2026 including dates, location, venue, and links.",
  "inputSchema": { "type": "object", "properties": {}, "required": [] }
}
```

**Response content:**

```json
{
  "name": "AI Engineer Europe 2026",
  "tagline": "The premier AI Engineering conference in Europe",
  "dates": "April 8-10, 2026",
  "location": "London, UK",
  "venue": "Park Plaza Westminster Bridge",
  "website": "https://ai.engineer/europe",
  "ticketUrl": "https://app.ai.engineer/e/ai-engineer-europe-2026/portal",
  "organizerTwitter": "https://x.com/aiDotEngineer",
  "youtube": "https://youtube.com/@aidotengineer",
  "linkedin": "https://www.linkedin.com/company/aidotengineer/",
  "newsletter": "https://ai.engineer/newsletter",
  "description": "AI Engineer Europe is a 3-day conference bringing together the best AI engineers, researchers, and builders in Europe. Day 1 features hands-on workshops, Days 2-3 feature keynotes, talks across multiple tracks (AI Agents, Code, Open Source, Product, Infra), expo, and networking."
}
```

### list_speakers

Returns all speakers, optionally filtered by search term.

```json
{
  "name": "list_speakers",
  "description": "List all confirmed speakers with their roles, companies, social links, and talk details.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "search": {
        "type": "string",
        "description": "Optional search term to filter speakers by name, company, or role."
      }
    },
    "required": []
  }
}
```

**Search behavior:** Filters on `name`, `company`, and `role` fields (case-insensitive substring match).

**Response content:** `{ "totalSpeakers": N, "speakers": [...] }`

### list_talks

Returns all talks, optionally filtered.

```json
{
  "name": "list_talks",
  "description": "List all confirmed talks/sessions with titles, descriptions, speakers, times, and rooms.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "day": {
        "type": "string",
        "description": "Optional day to filter by (e.g. \"April 8\", \"April 9\", \"April 10\")."
      },
      "type": {
        "type": "string",
        "description": "Optional type to filter by (e.g. \"workshop\", \"keynote\", \"talk\")."
      },
      "track": {
        "type": "string",
        "description": "Optional track to filter by (e.g. \"AI Agents\", \"Code\", \"Open Source\")."
      },
      "search": {
        "type": "string",
        "description": "Optional search term to filter talks by title or speaker name."
      }
    },
    "required": []
  }
}
```

**Filter behavior:**
- `day` — exact match on day string
- `type` — case-insensitive exact match
- `track` — case-insensitive substring match
- `search` — case-insensitive substring match on title and speaker names

Multiple filters are AND-ed together.

**Response content:** `{ "totalTalks": N, "talks": [...] }`

### get_schedule

Returns the schedule grouped by day.

```json
{
  "name": "get_schedule",
  "description": "Get the full conference schedule organized by day.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "day": {
        "type": "string",
        "description": "Optional day to filter by (e.g. \"April 8\", \"April 9\", \"April 10\")."
      }
    },
    "required": []
  }
}
```

**Response content:** `{ "days": [{ "day": "April 8", "sessions": [...] }, ...] }`

## JSON-RPC lifecycle

### 1. Initialize

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2025-03-26",
    "capabilities": {},
    "clientInfo": { "name": "my-client", "version": "1.0.0" }
  }
}
```

### 2. Notify initialized

```json
{
  "jsonrpc": "2.0",
  "method": "notifications/initialized"
}
```

### 3. List tools

```json
{ "jsonrpc": "2.0", "id": 2, "method": "tools/list" }
```

### 4. Call a tool

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "list_talks",
    "arguments": { "day": "April 9", "type": "keynote" }
  }
}
```

### Response format

Tool call responses wrap results in MCP content format:

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{ \"totalTalks\": 12, \"talks\": [...] }"
      }
    ]
  }
}
```

The `text` field contains JSON-stringified results.

## Error codes

| Code | Meaning |
|---|---|
| `-32700` | Parse error (empty body) |
| `-32600` | Invalid JSON-RPC version |
| `-32601` | Method not found |
| `-32602` | Invalid params (missing tool name, unknown tool) |

## Batch requests

Send an array of JSON-RPC requests:

```json
[
  { "jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": { "name": "get_conference_info", "arguments": {} } },
  { "jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": { "name": "list_speakers", "arguments": { "search": "Google" } } }
]
```

Returns an array of responses.

## Python client

Complete Python helper for calling MCP tools:

```python
import requests
import json
from typing import Any

MCP_URL = 'https://ai.engineer/europe/mcp'

def mcp_call(tool_name: str, arguments: dict[str, Any] | None = None) -> dict:
    """Call an MCP tool and return the parsed result."""
    resp = requests.post(MCP_URL, json={
        'jsonrpc': '2.0',
        'id': 1,
        'method': 'tools/call',
        'params': {'name': tool_name, 'arguments': arguments or {}}
    }, headers={
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    })
    resp.raise_for_status()
    data = resp.json()
    if 'error' in data:
        raise Exception(f"MCP error {data['error']['code']}: {data['error']['message']}")
    return json.loads(data['result']['content'][0]['text'])

def mcp_list_tools() -> list[dict]:
    """List all available MCP tools."""
    resp = requests.post(MCP_URL, json={
        'jsonrpc': '2.0', 'id': 1, 'method': 'tools/list'
    }, headers={'Content-Type': 'application/json'})
    return resp.json()['result']['tools']

# --- Examples ---

# List available tools
tools = mcp_list_tools()
for tool in tools:
    print(f"{tool['name']}: {tool['description']}")

# Get conference info
info = mcp_call('get_conference_info')
print(f"\n{info['name']} — {info['dates']} — {info['venue']}")

# Search speakers by company
speakers = mcp_call('list_speakers', {'search': 'Anthropic'})
print(f"\n{speakers['totalSpeakers']} speakers from Anthropic:")
for s in speakers['speakers']:
    talks = ', '.join(t['title'] for t in s.get('talks', []) if t.get('title'))
    print(f"  {s['name']} ({s.get('role', '?')}): {talks}")

# Get MCP track talks
mcp_talks = mcp_call('list_talks', {'track': 'MCP'})
print(f"\n{mcp_talks['totalTalks']} MCP track talks:")
for t in mcp_talks['talks']:
    print(f"  {t.get('time', '?')}: {t['title']} — {', '.join(t['speakers'])}")

# Get Day 2 schedule
schedule = mcp_call('get_schedule', {'day': 'April 9'})
for day in schedule['days']:
    print(f"\n--- {day['day']} ---")
    for session in day['sessions']:
        print(f"  {session.get('time', '?')}: {session.get('title', 'TBA')}")
```

## JavaScript/TypeScript client

```typescript
const MCP_URL = 'https://ai.engineer/europe/mcp';

async function mcpCall(toolName: string, args: Record<string, string> = {}) {
  const resp = await fetch(MCP_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
    body: JSON.stringify({
      jsonrpc: '2.0', id: 1,
      method: 'tools/call',
      params: { name: toolName, arguments: args },
    }),
  });
  const data = await resp.json();
  if (data.error) throw new Error(`MCP error ${data.error.code}: ${data.error.message}`);
  return JSON.parse(data.result.content[0].text);
}

// Get all keynotes
const keynotes = await mcpCall('list_talks', { type: 'keynote' });
console.log(keynotes.talks.map(t => `${t.time}: ${t.title}`));
```
