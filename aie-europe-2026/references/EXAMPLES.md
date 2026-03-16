# Usage Examples

Real-world examples of how to use the AI Engineer Europe 2026 APIs to build useful things. Each example includes both TypeScript and Python implementations.

The TypeScript examples mirror real patterns from the production codebase (`europe-public-data.ts`, `mcp.ts`, `llms-txt.ts`). The Python examples are equivalent implementations.

---

## 1. Build a "Who's Speaking About What" Topic Index

Cross-reference speakers with their talks to build a searchable topic index — useful for attendee guides, chatbots, or recommendation engines.

### TypeScript

~~~typescript
// Mirrors the real data-joining pattern from europe-public-data.ts:
// speakers are built by iterating schedule sessions and merging per-speaker data

type PublicTalk = {
  title?: string;
  description?: string;
  day?: string;
  time?: string;
  room?: string;
  type?: string;
  track?: string;
  speakers: string[];
};

type PublicSpeaker = {
  name: string;
  role?: string;
  company?: string;
  twitter?: string;
  photoUrl?: string;
  sessions: PublicTalk[];
};

type TopicEntry = {
  topic: string;
  speakers: { name: string; company?: string; talkTitle: string }[];
};

async function buildTopicIndex(): Promise<TopicEntry[]> {
  const res = await fetch('https://ai.engineer/europe/speakers.json');
  const { speakers }: { speakers: PublicSpeaker[] } = await res.json();

  const topicMap = new Map<string, TopicEntry['speakers']>();

  for (const speaker of speakers) {
    for (const talk of speaker.sessions) {
      const topics: string[] = [];
      if (talk.track) topics.push(talk.track);

      // Extract keywords from title
      const keywords = ['agents', 'mcp', 'rag', 'fine-tuning', 'open source',
        'inference', 'evaluation', 'safety', 'multimodal', 'code generation'];
      for (const kw of keywords) {
        if (talk.title?.toLowerCase().includes(kw)) topics.push(kw);
      }

      for (const topic of topics) {
        const key = topic.toLowerCase();
        const list = topicMap.get(key) ?? [];
        list.push({
          name: speaker.name,
          company: speaker.company,
          talkTitle: talk.title ?? 'TBA',
        });
        topicMap.set(key, list);
      }
    }
  }

  return Array.from(topicMap.entries())
    .map(([topic, speakers]) => ({ topic, speakers }))
    .sort((a, b) => b.speakers.length - a.speakers.length);
}

// Usage
const index = await buildTopicIndex();
for (const entry of index.slice(0, 10)) {
  console.log(`\n${entry.topic} (${entry.speakers.length} speakers):`);
  for (const s of entry.speakers) {
    console.log(`  ${s.name} (${s.company ?? '?'}): "${s.talkTitle}"`);
  }
}
~~~

### Python

~~~python
import requests
from collections import defaultdict

def build_topic_index() -> list[dict]:
    """Build a topic -> speakers index from conference data."""
    data = requests.get('https://ai.engineer/europe/speakers.json').json()

    keywords = ['agents', 'mcp', 'rag', 'fine-tuning', 'open source',
                'inference', 'evaluation', 'safety', 'multimodal', 'code generation']

    topic_map: dict[str, list[dict]] = defaultdict(list)

    for speaker in data['speakers']:
        for talk in speaker.get('sessions', []):
            topics = []
            if talk.get('track'):
                topics.append(talk['track'].lower())
            title = (talk.get('title') or '').lower()
            for kw in keywords:
                if kw in title:
                    topics.append(kw)

            for topic in topics:
                topic_map[topic].append({
                    'name': speaker['name'],
                    'company': speaker.get('company'),
                    'talk_title': talk.get('title', 'TBA'),
                })

    return sorted(
        [{'topic': t, 'speakers': s} for t, s in topic_map.items()],
        key=lambda x: len(x['speakers']),
        reverse=True,
    )

index = build_topic_index()
for entry in index[:10]:
    print(f"\n{entry['topic']} ({len(entry['speakers'])} speakers):")
    for s in entry['speakers']:
        print(f"  {s['name']} ({s['company'] or '?'}): \"{s['talk_title']}\"")
~~~

---

## 2. Semantic Search with Pre-Computed Gemini Embeddings

Use the pre-computed 128-dim [Gemini Embedding 2](https://ai.google.dev/gemini-api/docs/models/gemini-embedding-2-preview) vectors to build semantic search over speakers and sessions — no embedding API calls needed for the corpus. Vectors are truncated from 3072 to 128 dims via [Matryoshka Representation Learning (MRL)](https://ai.google.dev/gemini-api/docs/models/gemini-embedding-2-preview#controlling-embedding-size).

### TypeScript

~~~typescript
// Use pre-computed embeddings — no API key needed for the corpus.
// Only need Gemini API for generating query embeddings.

type EmbeddedSpeaker = {
  name: string; role?: string; company?: string;
  embedding: number[]; // 128-dim Gemini Embedding 2 (MRL)
};

function cosineSim(a: number[], b: number[]): number {
  let dot = 0, magA = 0, magB = 0;
  for (let i = 0; i < a.length; i++) {
    dot += a[i]! * b[i]!;
    magA += a[i]! * a[i]!;
    magB += b[i]! * b[i]!;
  }
  return dot / (Math.sqrt(magA) * Math.sqrt(magB));
}

// Fetch pre-computed speaker embeddings (128-dim, ~300KB)
const res = await fetch('https://ai.engineer/europe/speakers-embeddings.json');
const { speakers }: { speakers: EmbeddedSpeaker[] } = await res.json();

// Generate a query embedding using Gemini (same model + MRL dim)
async function embedQuery(text: string, apiKey: string): Promise<number[]> {
  const res = await fetch(
    `https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-2-preview:embedContent?key=${apiKey}`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'models/gemini-embedding-2-preview',
        content: { parts: [{ text }] },
        taskType: 'RETRIEVAL_QUERY',
        outputDimensionality: 128,
      }),
    }
  );
  const data = await res.json();
  return data.embedding.values;
}

// Search speakers by semantic similarity
const queryVec = await embedQuery('autonomous coding agents', process.env.GEMINI_API_KEY!);
const ranked = speakers
  .map(s => ({ name: s.name, company: s.company, score: cosineSim(queryVec, s.embedding) }))
  .sort((a, b) => b.score - a.score)
  .slice(0, 5);

for (const r of ranked) {
  console.log(`  [${r.score.toFixed(3)}] ${r.name} (${r.company ?? '?'})`);
}

// --- Same works for sessions ---
const sessRes = await fetch('https://ai.engineer/europe/sessions-embeddings.json');
const { sessions } = await sessRes.json();
const sessionRanked = sessions
  .map((s: any) => ({ title: s.title, speakers: s.speakers, score: cosineSim(queryVec, s.embedding) }))
  .sort((a: any, b: any) => b.score - a.score)
  .slice(0, 5);

for (const r of sessionRanked) {
  console.log(`  [${r.score.toFixed(3)}] ${r.title} — ${r.speakers.join(', ')}`);
}
~~~

### Python

~~~python
import requests
import numpy as np

# --- Load pre-computed embeddings (no API key needed) ---

data = requests.get('https://ai.engineer/europe/speakers-embeddings.json').json()
speakers = data['speakers']
# Each speaker has a 128-dim embedding from Gemini Embedding 2 (MRL)
speaker_vecs = np.array([s['embedding'] for s in speakers])  # shape: (N, 128)

def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

# --- Generate query embedding with Gemini API ---

def embed_query(text: str, api_key: str) -> np.ndarray:
    """Generate a 128-dim query embedding using Gemini Embedding 2 + MRL."""
    resp = requests.post(
        f'https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-2-preview:embedContent?key={api_key}',
        json={
            'model': 'models/gemini-embedding-2-preview',
            'content': {'parts': [{'text': text}]},
            'taskType': 'RETRIEVAL_QUERY',
            'outputDimensionality': 128,
        }
    )
    return np.array(resp.json()['embedding']['values'])

import os
query_vec = embed_query('autonomous coding agents', os.environ['GEMINI_API_KEY'])

# --- Semantic search ---

scores = [cosine_sim(query_vec, np.array(s['embedding'])) for s in speakers]
ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)

print('Top 5 speakers for "autonomous coding agents":')
for i, score in ranked[:5]:
    s = speakers[i]
    print(f"  [{score:.3f}] {s['name']} ({s.get('company', '?')})")

# --- Cluster speakers by expertise using pre-computed embeddings ---

from sklearn.cluster import KMeans

kmeans = KMeans(n_clusters=6, random_state=42, n_init=10)
labels = kmeans.fit_predict(speaker_vecs)

clusters: dict[int, list] = {}
for i, label in enumerate(labels):
    clusters.setdefault(label, []).append(speakers[i])

print('\n--- Speaker Clusters ---\n')
for label, members in sorted(clusters.items()):
    names = [s['name'] for s in members[:5]]
    companies = set(s.get('company', '?') for s in members if s.get('company'))
    print(f"Cluster {label} ({len(members)} speakers): {', '.join(names)}")
    print(f"  Companies: {', '.join(list(companies)[:5])}\n")
~~~

---

## 3. Multi-Track Day Planner: Optimize Your Conference Path

Days 2-3 run talks in parallel across 5-6 rooms. Fetch the schedule, group by time slot, and pick one talk per slot to maximize track coverage.

### TypeScript

~~~typescript
// Uses the same schedule-by-day logic as getScheduleByDay() in europe-public-data.ts

type PublicTalk = {
  title?: string; day?: string; time?: string; room?: string;
  type?: string; track?: string; speakers: string[];
};

async function getDayPlan(day: string) {
  const res = await fetch('https://ai.engineer/europe/sessions.json');
  const { sessions }: { sessions: PublicTalk[] } = await res.json();

  const dayTalks = sessions.filter((t) => t.day === day && t.type !== 'break');

  // Group by time slot - same Map pattern as llms-txt.ts
  const slotMap = new Map<string, PublicTalk[]>();
  for (const talk of dayTalks) {
    const time = talk.time ?? 'TBD';
    const list = slotMap.get(time) ?? [];
    list.push(talk);
    slotMap.set(time, list);
  }

  return Array.from(slotMap.entries())
    .map(([time, options]) => ({ time, options }))
    .sort((a, b) => a.time.localeCompare(b.time));
}

function pickByTrackPriority(
  slots: { time: string; options: PublicTalk[] }[],
  preferredTracks: string[]
): PublicTalk[] {
  const picks: PublicTalk[] = [];
  const tracksSeen = new Set<string>();

  for (const slot of slots) {
    if (slot.options.length === 1) {
      picks.push(slot.options[0]!);
      continue;
    }

    const sorted = [...slot.options].sort((a, b) => {
      const aSeen = tracksSeen.has(a.track ?? '') ? 1 : 0;
      const bSeen = tracksSeen.has(b.track ?? '') ? 1 : 0;
      if (aSeen !== bSeen) return aSeen - bSeen;
      const aIdx = preferredTracks.indexOf(a.track ?? '');
      const bIdx = preferredTracks.indexOf(b.track ?? '');
      return (aIdx === -1 ? 999 : aIdx) - (bIdx === -1 ? 999 : bIdx);
    });

    const pick = sorted[0]!;
    picks.push(pick);
    if (pick.track) tracksSeen.add(pick.track);
  }

  return picks;
}

const slots = await getDayPlan('April 9');
const picks = pickByTrackPriority(slots, ['AI Agents', 'MCP', 'Coding Agents', 'Open Source']);

console.log('Your optimized Day 2 schedule:\n');
for (const talk of picks) {
  console.log(`${talk.time} [${talk.room}] ${talk.title}`);
  console.log(`  Track: ${talk.track ?? 'Main'} | ${talk.speakers.join(', ')}\n`);
}
~~~

### Python

~~~python
import requests
from collections import defaultdict

def get_day_plan(day: str) -> list[dict]:
    """Get all time slots for a given day with parallel track options."""
    data = requests.get('https://ai.engineer/europe/sessions.json').json()

    day_sessions = [t for t in data['sessions']
                    if t.get('day') == day and t.get('type') != 'break']

    slots: dict[str, list] = defaultdict(list)
    for talk in day_sessions:
        slots[talk.get('time', 'TBD')].append(talk)

    return sorted(
        [{'time': t, 'options': opts} for t, opts in slots.items()],
        key=lambda s: s['time'],
    )

def pick_by_track_priority(slots: list[dict], preferred_tracks: list[str]) -> list[dict]:
    """Pick one talk per time slot, maximizing track diversity."""
    picks = []
    tracks_seen = set()

    for slot in slots:
        if len(slot['options']) == 1:
            picks.append(slot['options'][0])
            continue

        def score(talk):
            track = talk.get('track', '')
            seen_penalty = 1 if track in tracks_seen else 0
            try: pref_score = preferred_tracks.index(track)
            except ValueError: pref_score = 999
            return (seen_penalty, pref_score)

        pick = min(slot['options'], key=score)
        picks.append(pick)
        if pick.get('track'): tracks_seen.add(pick['track'])

    return picks

slots = get_day_plan('April 9')
picks = pick_by_track_priority(slots, ['AI Agents', 'MCP', 'Coding Agents', 'Open Source'])

print('Your optimized Day 2 schedule:\n')
for talk in picks:
    speakers = ', '.join(talk.get('speakers', []))
    print(f"{talk.get('time', '?')} [{talk.get('room', '?')}] {talk.get('title', 'TBA')}")
    print(f"  Track: {talk.get('track', 'Main')} | {speakers}\n")
~~~

---

## 4. Speaker Social Graph: "If You Liked This Speaker, Meet These People"

Find speakers who co-present (panels, joint talks) to surface collaboration-based recommendations. Unlike semantic similarity (#2), this uses _social signal_ — if two speakers chose to present together, their work is connected. Attendees can use this to discover related speakers they wouldn't find via topic search, and to identify networking clusters at the conference.

### TypeScript

~~~typescript
// In the real codebase, speakers are linked to talks via the schedule:
// each session has a speakers[] array, and getPublicSpeakers() merges
// all talks per speaker. This example reverses that to find co-speakers.

type PublicTalk = { title?: string; speakers: string[] };
type PublicSpeaker = { name: string; company?: string };
type Connection = {
  speakers: [string, string]; sharedTalks: string[];
  companies: [string?, string?];
};

async function buildSpeakerGraph(): Promise<Connection[]> {
  const [talksRes, spkRes] = await Promise.all([
    fetch('https://ai.engineer/europe/sessions.json'),
    fetch('https://ai.engineer/europe/speakers.json'),
  ]);
  const { sessions }: { sessions: PublicTalk[] } = await talksRes.json();
  const { speakers }: { speakers: PublicSpeaker[] } = await spkRes.json();

  const companyOf = new Map(speakers.map((s) => [s.name, s.company]));
  const connections = new Map<string, Connection>();

  for (const session of sessions) {
    if (session.speakers.length < 2) continue;

    for (let i = 0; i < session.speakers.length; i++) {
      for (let j = i + 1; j < session.speakers.length; j++) {
        const pair = [session.speakers[i]!, session.speakers[j]!].sort() as [string, string];
        const key = pair.join('|');

        const existing = connections.get(key) ?? {
          speakers: pair, sharedTalks: [],
          companies: [companyOf.get(pair[0]), companyOf.get(pair[1])],
        };
        if (session.title) existing.sharedTalks.push(session.title);
        connections.set(key, existing);
      }
    }
  }

  return Array.from(connections.values())
    .sort((a, b) => b.sharedTalks.length - a.sharedTalks.length);
}

const graph = await buildSpeakerGraph();
console.log(`Found ${graph.length} speaker connections:\n`);
for (const conn of graph) {
  const [a, b] = conn.speakers;
  const [coA, coB] = conn.companies;
  console.log(`${a} (${coA ?? '?'}) <-> ${b} (${coB ?? '?'})`);
  for (const title of conn.sharedTalks) {
    console.log(`  "${title}"`);
  }
}
~~~

### Python

~~~python
import requests
from itertools import combinations

def build_speaker_graph() -> list[dict]:
    """Find speakers who co-present talks to map the collaboration network."""
    sessions = requests.get('https://ai.engineer/europe/sessions.json').json()['sessions']
    speakers = requests.get('https://ai.engineer/europe/speakers.json').json()['speakers']

    company_of = {s['name']: s.get('company') for s in speakers}
    connections: dict[tuple, dict] = {}

    for session in sessions:
        spks = session.get('speakers', [])
        if len(spks) < 2:
            continue

        for a, b in combinations(sorted(spks), 2):
            key = (a, b)
            if key not in connections:
                connections[key] = {
                    'speakers': [a, b], 'shared_talks': [],
                    'companies': [company_of.get(a), company_of.get(b)],
                }
            if session.get('title'):
                connections[key]['shared_talks'].append(session['title'])

    return sorted(connections.values(),
                  key=lambda x: len(x['shared_talks']), reverse=True)

graph = build_speaker_graph()
print(f"Found {len(graph)} speaker connections:\n")
for conn in graph:
    a, b = conn['speakers']
    co_a, co_b = conn['companies']
    print(f"{a} ({co_a or '?'}) <-> {b} ({co_b or '?'})")
    for title in conn['shared_talks']:
        print(f'  "{title}"')
~~~
