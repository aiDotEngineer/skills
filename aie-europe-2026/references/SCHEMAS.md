# API Response Schemas

Full response structures for AI Engineer Europe 2026 endpoints.

## talks.json

**URL:** `GET https://ai.engineer/europe/talks.json`

### Response envelope

```json
{
  "conference": "AI Engineer Europe 2026",
  "dates": "April 8-10, 2026",
  "location": "London, UK",
  "website": "https://ai.engineer/europe",
  "totalTalks": 147,
  "talks": [ ... ]
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
  "talks": [
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

Speaker with multiple talks:

```json
{
  "name": "swyx",
  "role": "Founder",
  "company": "AI Engineer",
  "twitter": "https://x.com/swyx",
  "photoUrl": "https://ai.engineer/europe-speakers/swyx.jpg",
  "talks": [
    { "title": "Opening Keynote", "day": "April 9", ... },
    { "title": "Fireside Chat with swyx and Tuomas Artman", "day": "April 10", ... }
  ]
}
```

### Notes

- Speakers are sorted alphabetically by name
- Social links are full URLs when present, omitted when absent
- `photoUrl` follows the pattern `https://ai.engineer/europe-speakers/{filename}`
- A speaker's `talks` array contains the same `PublicTalk` objects as `talks.json`

---

## llms.txt

**URL:** `GET https://ai.engineer/europe/llms.txt`

Plain text. Contains: conference name, dates, location, venue, website, ticket URL, and a brief schedule overview. Optimized for LLM context windows — small and focused.

---

## llms-full.txt

**URL:** `GET https://ai.engineer/europe/llms-full.txt`

Plain text. Contains everything in `llms.txt` plus: every talk description, every speaker bio, full schedule with rooms and tracks. Larger payload but comprehensive.

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
