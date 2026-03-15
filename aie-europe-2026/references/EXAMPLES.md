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
  talks: PublicTalk[];
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
    for (const talk of speaker.talks) {
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
        for talk in speaker.get('talks', []):
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

## 2. Personal Schedule Builder with Conflict Detection

Fetch all talks, pick favorites by keyword, and detect time/room conflicts — the logic a schedule-builder app needs.

### TypeScript

~~~typescript
// Uses the same filtering pattern as the MCP list_talks tool in mcp.ts:
//   if (day) talks = talks.filter((t) => t.day === day);
//   if (type) talks = talks.filter((t) => t.type?.toLowerCase() === type.toLowerCase());

type PublicTalk = {
  title?: string; description?: string; day?: string; time?: string;
  room?: string; type?: string; track?: string; speakers: string[];
};

type Conflict = { day: string; time: string; talks: PublicTalk[] };

async function findConflicts(favoriteTalkTitles: string[]): Promise<Conflict[]> {
  const res = await fetch('https://ai.engineer/europe/talks.json');
  const { talks }: { talks: PublicTalk[] } = await res.json();

  const favorites = talks.filter((t) =>
    favoriteTalkTitles.some((fav) =>
      t.title?.toLowerCase().includes(fav.toLowerCase())
    )
  );

  // Group by day + time to detect conflicts
  const slotMap = new Map<string, PublicTalk[]>();
  for (const talk of favorites) {
    const key = `${talk.day}|${talk.time}`;
    const list = slotMap.get(key) ?? [];
    list.push(talk);
    slotMap.set(key, list);
  }

  return Array.from(slotMap.entries())
    .filter(([_, talks]) => talks.length > 1)
    .map(([key, talks]) => {
      const [day, time] = key.split('|');
      return { day: day!, time: time!, talks };
    });
}

const conflicts = await findConflicts(['MCP', 'agents', 'open source', 'infrastructure']);
if (conflicts.length === 0) {
  console.log('No conflicts!');
} else {
  for (const c of conflicts) {
    console.log(`\nConflict on ${c.day} at ${c.time}:`);
    for (const t of c.talks) {
      console.log(`  [${t.room}] ${t.title} - ${t.speakers.join(', ')}`);
    }
  }
}
~~~

### Python

~~~python
import requests
from collections import defaultdict

def find_conflicts(favorite_keywords: list[str]) -> list[dict]:
    """Find scheduling conflicts among your favorite talks."""
    data = requests.get('https://ai.engineer/europe/talks.json').json()

    favorites = [
        t for t in data['talks']
        if any(kw.lower() in (t.get('title') or '').lower() for kw in favorite_keywords)
    ]

    slots: dict[str, list[dict]] = defaultdict(list)
    for talk in favorites:
        key = f"{talk.get('day')}|{talk.get('time')}"
        slots[key].append(talk)

    return [
        {'day': k.split('|')[0], 'time': k.split('|')[1], 'talks': v}
        for k, v in slots.items() if len(v) > 1
    ]

conflicts = find_conflicts(['MCP', 'agents', 'open source', 'infrastructure'])
if not conflicts:
    print('No conflicts!')
else:
    for c in conflicts:
        print(f"\nConflict on {c['day']} at {c['time']}:")
        for t in c['talks']:
            speakers = ', '.join(t.get('speakers', []))
            print(f"  [{t.get('room', '?')}] {t.get('title', 'TBA')} - {speakers}")
~~~

---

## 3. Company Leaderboard: Who's Sending the Most Speakers?

Join speakers with their companies to build a leaderboard — great for "which companies are most active in the AI engineering community" analysis.

### TypeScript

~~~typescript
// Uses the real PublicSpeaker type - company comes from the raw schedule's
// speaker.company.name field, merged in getPublicSpeakers()

type PublicSpeaker = {
  name: string; role?: string; company?: string; companyDescription?: string;
  twitter?: string; talks: { title?: string; type?: string; track?: string }[];
};

type CompanyStats = {
  company: string; description?: string; speakerCount: number;
  talkCount: number; speakers: string[]; tracks: string[]; hasKeynote: boolean;
};

async function getCompanyLeaderboard(): Promise<CompanyStats[]> {
  const res = await fetch('https://ai.engineer/europe/speakers.json');
  const { speakers }: { speakers: PublicSpeaker[] } = await res.json();

  const companyMap = new Map<string, CompanyStats>();

  for (const s of speakers) {
    if (!s.company) continue;
    const key = s.company.toLowerCase();

    const existing = companyMap.get(key) ?? {
      company: s.company, description: s.companyDescription,
      speakerCount: 0, talkCount: 0, speakers: [], tracks: [], hasKeynote: false,
    };

    existing.speakerCount++;
    existing.speakers.push(s.name);
    existing.talkCount += s.talks.length;

    for (const talk of s.talks) {
      if (talk.track && !existing.tracks.includes(talk.track)) existing.tracks.push(talk.track);
      if (talk.type === 'keynote') existing.hasKeynote = true;
    }

    companyMap.set(key, existing);
  }

  return Array.from(companyMap.values())
    .sort((a, b) => b.speakerCount - a.speakerCount);
}

const leaderboard = await getCompanyLeaderboard();
console.log('Company Leaderboard\n');
for (const [i, c] of leaderboard.slice(0, 15).entries()) {
  const keynote = c.hasKeynote ? ' * keynote' : '';
  console.log(`${i + 1}. ${c.company} - ${c.speakerCount} speakers, ${c.talkCount} talks${keynote}`);
  console.log(`   Speakers: ${c.speakers.join(', ')}`);
  console.log(`   Tracks: ${c.tracks.join(', ') || 'N/A'}`);
}
~~~

### Python

~~~python
import requests

def company_leaderboard() -> list[dict]:
    """Rank companies by number of speakers at the conference."""
    data = requests.get('https://ai.engineer/europe/speakers.json').json()
    companies: dict[str, dict] = {}

    for speaker in data['speakers']:
        company = speaker.get('company')
        if not company:
            continue
        key = company.lower()

        if key not in companies:
            companies[key] = {
                'company': company, 'description': speaker.get('companyDescription'),
                'speaker_count': 0, 'talk_count': 0, 'speakers': [],
                'tracks': set(), 'has_keynote': False,
            }

        entry = companies[key]
        entry['speaker_count'] += 1
        entry['speakers'].append(speaker['name'])
        entry['talk_count'] += len(speaker.get('talks', []))

        for talk in speaker.get('talks', []):
            if talk.get('track'): entry['tracks'].add(talk['track'])
            if talk.get('type') == 'keynote': entry['has_keynote'] = True

    result = sorted(companies.values(), key=lambda x: x['speaker_count'], reverse=True)
    for r in result:
        r['tracks'] = sorted(r['tracks'])
    return result

leaderboard = company_leaderboard()
print('Company Leaderboard\n')
for i, c in enumerate(leaderboard[:15], 1):
    keynote = ' * keynote' if c['has_keynote'] else ''
    print(f"{i}. {c['company']} - {c['speaker_count']} speakers, {c['talk_count']} talks{keynote}")
    print(f"   Speakers: {', '.join(c['speakers'])}")
    print(f"   Tracks: {', '.join(c['tracks']) or 'N/A'}")
~~~

---

## 4. Multi-Track Day Planner: Optimize Your Conference Path

Days 2-3 run talks in parallel across 5-6 rooms. Fetch the schedule, group by time slot, and pick one talk per slot to maximize track coverage.

### TypeScript

~~~typescript
// Uses the same schedule-by-day logic as getScheduleByDay() in europe-public-data.ts

type PublicTalk = {
  title?: string; day?: string; time?: string; room?: string;
  type?: string; track?: string; speakers: string[];
};

async function getDayPlan(day: string) {
  const res = await fetch('https://ai.engineer/europe/talks.json');
  const { talks }: { talks: PublicTalk[] } = await res.json();

  const dayTalks = talks.filter((t) => t.day === day && t.type !== 'break');

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
    data = requests.get('https://ai.engineer/europe/talks.json').json()

    day_talks = [t for t in data['talks']
                 if t.get('day') == day and t.get('type') != 'break']

    slots: dict[str, list] = defaultdict(list)
    for talk in day_talks:
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

## 5. Speaker Social Graph: Map Connections via Co-Presentations

Find speakers who present together (panels, joint talks) to build a collaboration graph — useful for networking recommendations or community analysis.

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
    fetch('https://ai.engineer/europe/talks.json'),
    fetch('https://ai.engineer/europe/speakers.json'),
  ]);
  const { talks }: { talks: PublicTalk[] } = await talksRes.json();
  const { speakers }: { speakers: PublicSpeaker[] } = await spkRes.json();

  const companyOf = new Map(speakers.map((s) => [s.name, s.company]));
  const connections = new Map<string, Connection>();

  for (const talk of talks) {
    if (talk.speakers.length < 2) continue;

    for (let i = 0; i < talk.speakers.length; i++) {
      for (let j = i + 1; j < talk.speakers.length; j++) {
        const pair = [talk.speakers[i]!, talk.speakers[j]!].sort() as [string, string];
        const key = pair.join('|');

        const existing = connections.get(key) ?? {
          speakers: pair, sharedTalks: [],
          companies: [companyOf.get(pair[0]), companyOf.get(pair[1])],
        };
        if (talk.title) existing.sharedTalks.push(talk.title);
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
    talks = requests.get('https://ai.engineer/europe/talks.json').json()['talks']
    speakers = requests.get('https://ai.engineer/europe/speakers.json').json()['speakers']

    company_of = {s['name']: s.get('company') for s in speakers}
    connections: dict[tuple, dict] = {}

    for talk in talks:
        spks = talk.get('speakers', [])
        if len(spks) < 2:
            continue

        for a, b in combinations(sorted(spks), 2):
            key = (a, b)
            if key not in connections:
                connections[key] = {
                    'speakers': [a, b], 'shared_talks': [],
                    'companies': [company_of.get(a), company_of.get(b)],
                }
            if talk.get('title'):
                connections[key]['shared_talks'].append(talk['title'])

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
