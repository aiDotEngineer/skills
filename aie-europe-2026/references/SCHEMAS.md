# API Response Schemas

Full response structures for AI Engineer Europe 2026 endpoints.

## sessions.json

**URL:** `GET https://ai.engineer/europe/sessions.json`

### Response envelope

```json
{
  "conference": "AI Engineer Europe 2026",
  "dates": "April 8-10, 2026",
  "location": "London, UK",
  "website": "https://ai.engineer/europe",
  "totalSessions": 147,
  "sessions": [ ... ]
}
```

### Talk object

```json
{
  "title": "The GenAI Divide",
  "day": "April 9",
  "time": "9:15-9:30am",
  "room": "Keynote",
  "type": "keynote",
  "speakers": ["Aditya Challapally"]
}
```

Full talk with description:

```json
{
  "title": "Bringing MCPs to the Enterprise",
  "description": "MCPs are often flaky, face multiple security vulnerabilities, and are generally hard to scale. Most enterprises struggle to use more than single digit numbers of MCPs due to issues with security, observability, and access control. In this talk, we'll explore the approaches and learnings we at Anthropic have been taking to solve this, and make MCPs more enterprise ready.",
  "day": "April 10",
  "time": "3:10-3:30pm",
  "room": "St. James",
  "type": "talk",
  "track": "MCP",
  "speakers": ["Karan Sampath"]
}
```

### Field values

**`day`** — One of:
- `"April 8"` (Day 1 — Workshops)
- `"April 9"` (Day 2 — Main conference)
- `"April 10"` (Day 3 — Main conference)

**`type`** — One of:
- `"keynote"` — Main stage keynotes
- `"talk"` — Track talks (25-40 min)
- `"workshop"` — Day 1 hands-on workshops
- `"panel"` — Panel discussions
- `"break"` — Breaks, lunch, networking

**`room`** — One of:
- `"Keynote"` — Main stage (Days 2-3)
- `"Abbey"` — Track room
- `"Fleming"` — Track room
- `"Moore"` — Track room
- `"St. James"` — Track room
- `"Westminster"` — Track room

**`track`** — Day 2-3 only. Values include:
- `"AI Agents"`
- `"Coding Agents"`
- `"MCP"`
- `"Open Source"`
- `"GPUs & LLM Infrastructure"`
- `"Generative Media"`
- `"AI Architects"`
- `"Product"`

---

## speakers.json

**URL:** `GET https://ai.engineer/europe/speakers.json`

### Response envelope

```json
{
  "conference": "AI Engineer Europe 2026",
  "dates": "April 8-10, 2026",
  "location": "London, UK",
  "website": "https://ai.engineer/europe",
  "totalSpeakers": 152,
  "speakers": [ ... ]
}
```

### Speaker object

```json
{
  "name": "Aditya Challapally",
  "role": "Lead Author",
  "company": "MIT",
  "companyDescription": "Massachusetts Institute of Technology",
  "twitter": "https://x.com/AChallapally",
  "linkedin": "https://www.linkedin.com/in/adityachallapally/",
  "photoUrl": "https://ai.engineer/europe-speakers/aditya-challapally.jpg",
  "sessions": [
    {
      "title": "The GenAI Divide",
      "day": "April 9",
      "time": "9:15-9:30am",
      "room": "Keynote",
      "type": "keynote",
      "speakers": ["Aditya Challapally"]
    }
  ]
}
```

Speaker with multiple sessions:

```json
{
  "name": "swyx",
  "role": "Founder",
  "company": "AI Engineer",
  "twitter": "https://x.com/swyx",
  "photoUrl": "https://ai.engineer/europe-speakers/swyx.jpg",
  "sessions": [
    { "title": "Opening Keynote", "day": "April 9", ... },
    { "title": "Fireside Chat with swyx and Tuomas Artman", "day": "April 10", ... }
  ]
}
```

### Notes

- Speakers are sorted alphabetically by name
- Social links are full URLs when present, omitted when absent
- `photoUrl` follows the pattern `https://ai.engineer/europe-speakers/{filename}`
- A speaker's `sessions` array contains the same `PublicTalk` objects as `sessions.json`

---

## llms.txt

**URL:** `GET https://ai.engineer/europe/llms.txt`

Plain text. Contains: conference name, dates, location, venue, website, ticket URL, and a brief schedule overview. Optimized for LLM context windows — small and focused.

---

## llms-full.txt

**URL:** `GET https://ai.engineer/europe/llms-full.txt`

Plain text. Contains everything in `llms.txt` plus: every talk description, every speaker bio, full schedule with rooms and tracks. Larger payload but comprehensive.

---

## Python dataclasses

Optional typed wrappers for working with the API in Python:

```python
from dataclasses import dataclass, field
from urllib.request import urlopen
import json

@dataclass
class Talk:
    title: str = ''
    description: str = ''
    day: str = ''
    time: str = ''
    room: str = ''
    type: str = ''
    track: str = ''
    speakers: list[str] = field(default_factory=list)

@dataclass
class Speaker:
    name: str = ''
    role: str = ''
    company: str = ''
    companyDescription: str = ''
    twitter: str = ''
    linkedin: str = ''
    github: str = ''
    website: str = ''
    photoUrl: str = ''
    sessions: list[Talk] = field(default_factory=list)

    def __post_init__(self):
        self.sessions = [Talk(**t) if isinstance(t, dict) else t for t in self.sessions]

def fetch_sessions() -> list[Talk]:
    data = json.loads(urlopen('https://ai.engineer/europe/sessions.json').read())
    return [Talk(**t) for t in data['sessions']]

def fetch_speakers() -> list[Speaker]:
    data = json.loads(urlopen('https://ai.engineer/europe/speakers.json').read())
    return [Speaker(**s) for s in data['speakers']]

# Usage
sessions = fetch_sessions()
keynotes = [s for s in sessions if s.type == 'keynote']
for k in keynotes:
    print(f"{k.time}: {k.title} — {', '.join(k.speakers)}")

speakers = fetch_speakers()
for s in speakers:
    if s.company and 'google' in s.company.lower():
        print(f"{s.name} ({s.role}) — {len(s.sessions)} sessions")
```

---

## Common response headers

All JSON endpoints return:

```
Content-Type: application/json; charset=utf-8
Cache-Control: public, s-maxage=3600, stale-while-revalidate=86400
Access-Control-Allow-Origin: *
```

Text endpoints return:

```
Content-Type: text/plain; charset=utf-8
Cache-Control: public, s-maxage=3600, stale-while-revalidate=86400
```
