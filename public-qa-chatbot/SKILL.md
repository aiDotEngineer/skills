---
name: public-qa-chatbot
description: >
  Best practices for building an unauthenticated public Q&A chatbot widget.
  Covers rate limiting, security hardening, cost optimization, semantic caching,
  observability, UX patterns, and architecture. Tech-agnostic with concrete
  examples from a production implementation.
license: MIT
compatibility: Any web framework with a server-side API route
metadata:
  author: aidotengineer
  version: "1.0"
  category: "chatbot"
  tags: "rate-limiting, security, caching, observability, LLM"
---

# Public Q&A Chatbot — Best Practices

A comprehensive skill for building unauthenticated, public-facing Q&A chatbot widgets on marketing sites, conference pages, documentation portals, and similar contexts where you need to serve anonymous visitors while controlling cost and abuse.

Distilled from a production implementation powering the [AI Engineer Europe 2026](https://ai.engineer/europe) conference chatbot.

## When to use this skill

- Embedding a chatbot widget on a public website (no user login required)
- Answering questions from a known FAQ / knowledge base
- Serving anonymous visitors with LLM-powered responses
- Needing to protect against abuse, cost overruns, and API quota exhaustion
- Building a constrained Q&A bot (not a general-purpose assistant)

## Tech stack choices

This skill is written to be tech-agnostic. The reference implementation uses the stack below, but each component is swappable:

| Component | Reference choice | Alternatives |
|---|---|---|
| **LLM provider** | Gemini 3.1 Flash-Lite (via `@ai-sdk/google`) | OpenAI GPT-4o-mini, Anthropic Claude Haiku, Mistral, Llama via Groq/Together |
| **AI SDK** | Vercel AI SDK v6 (`ai`) | LangChain, LlamaIndex, direct provider SDKs |
| **Hosting** | Vercel (serverless functions) | Cloudflare Workers, AWS Lambda, Railway, Fly.io, Render |
| **Rate limiting** | Upstash Redis (`@upstash/ratelimit`) | Cloudflare Rate Limiting, AWS WAF, Redis (self-hosted), Arcjet |
| **Semantic cache** | Upstash Vector + Gemini Embeddings | Pinecone, Weaviate, Qdrant, pgvector, Cloudflare Vectorize |
| **Embedding model** | Gemini `text-embedding-004` (128 dims) | OpenAI `text-embedding-3-small`, Cohere Embed v3, Voyage AI |
| **Observability** | Braintrust (`wrapAISDK`) | Langfuse, Helicone, LangSmith, OpenTelemetry, Datadog LLM Obs |
| **Frontend** | React (inline component) | Vue, Svelte, vanilla JS, Web Components |

---

## 1. Rate Limiting

### Multi-layer rate limits

Apply limits at multiple granularities to prevent abuse:

- **Per-turn**: Cap messages per conversation (e.g. 3 turns/session)
- **Per-visitor per day**: Cap sessions per IP per day (e.g. 5/day)
- **Global per day**: Cap total sessions across all visitors (e.g. 1000/day)

```typescript
// Example constants
const LIMITS = {
  turnsPerSession: 3,
  sessionsPerVisitorPerDay: 5,
  globalSessionsPerDay: 1000,
};
```

### Use distributed rate limiting in production

In-memory rate limiting resets on every serverless cold start and isn't shared across instances. Use a distributed store for production:

**Upstash Redis (reference):**
```typescript
import { Ratelimit } from "@upstash/ratelimit";
import { Redis } from "@upstash/redis";

const redis = new Redis({ url: REDIS_URL, token: REDIS_TOKEN });
const limiter = new Ratelimit({
  redis,
  limiter: Ratelimit.slidingWindow(5, "1 d"), // 5 per day
  prefix: "chatbot:visitor",
});
const { success } = await limiter.limit(clientIp);
```

**Alternatives:**
- **Cloudflare Rate Limiting** — built into Cloudflare Workers, no external DB needed
- **Arcjet** — drop-in rate limiting SDK with bot detection
- **AWS WAF** — rate-based rules at the edge
- **Self-hosted Redis** — `ioredis` + custom sliding window logic

Always keep an in-memory fallback for local development:
```typescript
const useDistributed = !!redisUrl && !!redisToken;
if (!useDistributed) {
  // Fall back to in-memory Map for local dev
}
```

### Server-authoritative counting

Never trust client-reported turn counts or session flags. The server must count turns from the `messages` array itself:

```typescript
// Server counts turns — never trust client-reported values
const userTurnCount = messages.filter(m => m.role === "user").length;
const isNewSession = userTurnCount <= 1;
```

### BYOK (Bring Your Own Key) fallback

When rate-limited, let users input their own API key to continue chatting. This turns abuse into the user's own cost while preserving good UX:

```typescript
// Skip rate limiting when user provides their own key
if (!userApiKey) {
  const limit = await checkRateLimit(ip, turnCount, isNewSession);
  if (!limit.allowed) {
    return res.status(429).json({ error: limit.reason, rateLimited: true });
  }
}
const apiKey = userApiKey || serverKey;
```

Provide a direct link to obtain a key (e.g. https://aistudio.google.com/apikey for Gemini, https://platform.openai.com/api-keys for OpenAI).

---

## 2. Security

### Origin validation

Check the `Origin` or `Referer` header against an allowlist. This prevents cross-site request abuse where third parties embed scripts that burn your API quota:

```typescript
const origin = req.headers.origin ?? req.headers.referer ?? "";
const allowedHosts = ["localhost", "yourdomain.com", "vercel.app"];
if (origin && !allowedHosts.some(h => origin.includes(h))) {
  return res.status(403).json({ error: "Forbidden" });
}
```

> **Note:** Substring matching (`origin.includes(h)`) is acceptable for v1 but could theoretically match crafted domains. For stricter validation, parse the URL and compare the hostname.

### Input size limits

Cap both the number of messages and individual message length to prevent token-stuffing attacks that run up your LLM bill:

```typescript
const MAX_MESSAGES = 10;
const MAX_MESSAGE_LENGTH = 2000;

const trimmedMessages = messages.slice(-MAX_MESSAGES).map(m => ({
  ...m,
  parts: m.parts.map(p =>
    p.type === "text" && typeof p.text === "string"
      ? { ...p, text: p.text.slice(0, MAX_MESSAGE_LENGTH) }
      : p
  ),
}));
```

Also limit model output: `maxOutputTokens: 500` for short Q&A answers.

### Validate all parameters

Never trust `as` casts for user-supplied values. Validate against a known set:

```typescript
const VALID_PAGES = new Set(["europe", "home", "worldsfair"]);
if (!VALID_PAGES.has(page)) {
  return res.status(400).json({ error: "Invalid page parameter." });
}
```

### Safe error handling

- Never leak raw SDK error strings to the client (may contain API keys from BYOK)
- Never log full error objects (may contain sensitive data)
- Return generic error messages:

```typescript
} catch {
  console.error("Chat API error");
  return res.status(500).json({
    error: "An error occurred processing your request. Please try again.",
  });
}
```

### IP resolution on serverless platforms

Use the platform's trusted headers. On Vercel: `x-real-ip` > `x-vercel-forwarded-for` > `x-forwarded-for`. The standard `x-forwarded-for` is spoofable by clients.

**Alternatives:**
- **Cloudflare:** `CF-Connecting-IP`
- **AWS ALB/CloudFront:** `X-Forwarded-For` (first IP is trustworthy when set by AWS)
- **Fastly:** `Fastly-Client-IP`

### Disable non-text modalities

If you only need text responses, explicitly restrict the model:

```typescript
const model = provider("gemini-3.1-flash-lite", {
  responseModalities: ["TEXT"],     // Gemini-specific
  // For OpenAI: modalities: ["text"]
});
```

Also state "text-only assistant" in the system prompt as a defense-in-depth measure.

---

## 3. Cost Optimization

### Semantic caching

Use vector similarity search to cache and reuse responses for semantically similar questions. Most effective for FAQ-style chatbots where users ask the same questions in different words.

**Upstash Vector (reference):**
```typescript
import { Index } from "@upstash/vector";

const vectorIndex = new Index({ url: VECTOR_URL, token: VECTOR_TOKEN });

// Lookup: check cache before calling LLM
const results = await vectorIndex.query({
  vector: await getEmbedding(question),
  topK: 1,
  includeMetadata: true,
  filter: `page = '${page}'`,
});
if (results[0]?.score >= 0.92 && results[0]?.metadata?.answer) {
  return results[0].metadata.answer; // Cache hit — skip LLM call
}

// Store: cache after LLM responds (fire-and-forget)
void vectorIndex.upsert({
  id: `cache-${Date.now()}`,
  vector: embedding,
  metadata: { question, answer, page },
});
```

**Key decisions:**
- **Similarity threshold**: 0.92+ to avoid returning wrong cached answers. Lower values increase hit rate but risk incorrect responses.
- **Embedding dimensions**: 128 dims is sufficient for FAQ similarity and cheaper to compute/store than full 768/1536/3072.
- **Cache scope**: Cache first-turn questions only (highest hit rate, simplest implementation).
- **TTL**: 7 days is reasonable; stale answers are better than no cache.

**Alternatives:**
- **Pinecone** — managed vector DB with metadata filtering
- **pgvector** — if you already have PostgreSQL
- **Cloudflare Vectorize** — edge-native, pairs with Workers
- **Qdrant/Weaviate** — self-hosted or cloud, richer query capabilities

### FAQ list view

Offer a browsable FAQ list alongside the chat interface. This serves users who have common questions without making any LLM calls at all:

```typescript
// Structured FAQ data for UI rendering
export const FAQ_QUESTIONS: Array<{
  category: string;
  question: string;
  answer: string;
}> = [
  { category: "Ticketing", question: "Can I get a refund?", answer: "Yes, per our refund policy..." },
  // ...
];
```

Organize by category with expandable sections. Clicking a question can either show the pre-written answer directly or send it to the chat for a more detailed LLM response.

### Use the cheapest sufficient model

For a constrained Q&A chatbot, you rarely need the most powerful model:

| Model | Input cost | Output cost | Best for |
|---|---|---|---|
| Gemini 3.1 Flash-Lite | $0.25/1M | $1.50/1M | Cheapest, good for FAQ |
| GPT-4o-mini | $0.15/1M | $0.60/1M | Good balance of cost/quality |
| Claude Haiku | $0.25/1M | $1.25/1M | Fast, good at following instructions |
| Llama 3.3 70B (via Groq) | Free tier available | Free tier available | Cost-sensitive prototypes |

### Short output limits

Set `maxOutputTokens` to the minimum needed (e.g. 500 tokens for 2-4 sentence answers). This caps cost per request and keeps responses concise.

### Context caching

Pre-build and cache the system prompt context at module level. This avoids re-computing expensive string concatenations on every request:

```typescript
let cachedContext: Record<string, string> | null = null;

function buildContext(): Record<string, string> {
  if (cachedContext) return cachedContext;
  // ... expensive computation ...
  cachedContext = result;
  return cachedContext;
}
```

---

## 4. Observability

### Trace every LLM call

Instrument all LLM calls with input/output, latency, token usage, and cost. This is essential for monitoring abuse, debugging, and cost tracking.

**Braintrust (reference):**
```typescript
import { initLogger, wrapAISDK } from "braintrust";
initLogger({ projectName: "my-chatbot", apiKey: BRAINTRUST_API_KEY });
const { streamText } = wrapAISDK(ai); // Auto-traces all calls
```

**Alternatives:**
- **Langfuse** — open-source, self-hostable, supports OpenAI/Anthropic/custom
- **Helicone** — proxy-based, zero-code integration
- **LangSmith** — if using LangChain
- **OpenTelemetry** — vendor-neutral, export to Datadog/Honeycomb/Grafana
- **Datadog LLM Observability** — if already using Datadog

### Log semantic cache hits

Track cache hit rates to understand cost savings and tune the similarity threshold. A cache hit is a "free" response that saved an LLM call.

### Don't log sensitive data

Avoid logging full error objects, API keys, or user PII. Log just enough to debug (error type, status codes, IP hashes).

---

## 5. UX Patterns

### Markdown rendering

Enable markdown in chat responses and instruct the model to use it via the system prompt:

```
You may use markdown formatting in your responses when appropriate:
- Use **bold** for emphasis on key information like dates, prices, or venue names
- Use [links](url) when referencing websites
- Use bullet points for lists of speakers, sessions, or options
- Keep formatting light and readable
```

**React:** `react-markdown` + `remark-gfm`
**Vue:** `vue-markdown-render`
**Vanilla JS:** `marked` or `markdown-it`

### Draggable and resizable window

Let users reposition and resize the chat window. Persist geometry to `localStorage` so it survives page reloads. Clamp positions to viewport bounds:

```typescript
const newX = Math.max(0, Math.min(
  e.clientX - dragOffset.x,
  window.innerWidth - geometry.width
));
```

### Streaming responses

Always stream responses for perceived speed. Use your SDK's streaming API rather than waiting for the full response. The first token appearing quickly matters more than total latency.

### Graceful degradation

Every optional service should have a fallback:

| Service | If unavailable... |
|---|---|
| Redis (rate limiting) | Fall back to in-memory counters |
| Vector DB (cache) | Skip semantic caching, always call LLM |
| Observability (tracing) | Skip tracing, log locally |
| Server API key | Prompt user for BYOK |

```typescript
// Pattern: optional service with graceful fallback
const vectorIndex = vectorUrl && vectorToken
  ? new Index({ url: vectorUrl, token: vectorToken })
  : null;  // null = skip caching

if (vectorIndex) { /* try cache */ }
// Always falls through to LLM call
```

### Hover previews

Show top FAQ questions on hover over the chat bubble. This gives users an immediate sense of what the chatbot can help with and reduces "what do I ask?" friction.

---

## 6. Architecture

### Pluggable component

Design the chatbot as a single component that accepts props so it can be dropped into any page with different branding/context:

```tsx
<Chatbot
  page="europe"
  accentColor="#7C3AED"
  title="AI Engineer Europe Assistant"
/>
```

### Tool calls instead of context stuffing

Instead of stuffing all data into the system prompt, expose tools that the model can call on-demand. This keeps the context window smaller and responses more accurate:

```typescript
tools: {
  search_speakers: tool({
    description: "Search for speakers by name, company, or role",
    inputSchema: jsonSchema<{ search?: string }>({ ... }),
    execute: async (args) => searchSpeakers(args),
  }),
  search_sessions: tool({
    description: "Search sessions by title, speaker, day, type, or track",
    inputSchema: jsonSchema<{ search?: string; day?: string }>({ ... }),
    execute: async (args) => searchSessions(args),
  }),
}
```

### System prompt structure

Structure the system prompt with these sections in order:

1. **Role and constraints** — "You are the conference assistant..."
2. **Formatting instructions** — "Use markdown when appropriate..."
3. **Tool usage guidance** — "Use tools to search speakers/sessions..."
4. **Hard constraints** — "Text-only, no images/audio..."
5. **Fallback instructions** — "If you don't know, suggest emailing..."
6. **Reference data** — FAQ text, speaker list, session list

### API route, not edge function

For chatbot endpoints that need streaming + external service calls (Redis, Vector DB, observability), use a standard API route / serverless function rather than edge functions. Edge functions have stricter size/dependency limits and cold start characteristics that can cause issues with multiple SDK imports.

---

## 7. Knowledge Base Management

### Structured FAQ data

Maintain two representations of FAQ data:

1. **Flat text for the system prompt** — a single string the model reads as context
2. **Structured objects for the UI** — typed array with `question`, `answer`, `category` fields for rendering the FAQ list view

```typescript
// System prompt context (flat text)
export const FAQ_KNOWLEDGE_BASE = `
## TICKETING & PRICING
Q: Can I get a refund?
A: Yes, per our refund policy...
`;

// UI list view (structured)
export const FAQ_QUESTIONS = [
  { category: "Ticketing", question: "Can I get a refund?", answer: "Yes..." },
];
```

### Include venue/logistics details

Always include practical information (venue name, address, dates, ticket URLs) directly in the context. These are the most common questions and should never require a tool call.

---

## 8. Checklist

Use this checklist when building a new public Q&A chatbot:

- [ ] Rate limiting: per-turn, per-visitor, and global limits
- [ ] Distributed rate limiter for production (not in-memory only)
- [ ] Origin/CSRF validation on the API endpoint
- [ ] Input size limits (message count + message length)
- [ ] Server-authoritative turn counting (don't trust the client)
- [ ] Safe error handling (no SDK error leaks, no PII in logs)
- [ ] Correct IP resolution for your hosting platform
- [ ] BYOK fallback for rate-limited users
- [ ] Semantic caching for first-turn questions
- [ ] FAQ list view to reduce LLM calls
- [ ] Observability/tracing on all LLM calls
- [ ] Streaming responses for perceived speed
- [ ] Markdown rendering in chat responses
- [ ] Text-only modality restriction
- [ ] Graceful degradation when optional services are down
- [ ] System prompt with role, constraints, formatting, tools, and reference data
- [ ] No API keys exposed to the frontend

## Links

- Reference implementation: [github.com/aiDotEngineer/aiecode2025](https://github.com/aiDotEngineer/aiecode2025) (see `src/pages/api/chat.ts` and `src/components/Chatbot.tsx`)
- Agent Skills spec: [agentskills.io/specification](https://agentskills.io/specification)
- Vercel AI SDK: [sdk.vercel.ai](https://sdk.vercel.ai)
- Upstash: [upstash.com](https://upstash.com)
- Braintrust: [braintrust.dev](https://braintrust.dev)
- Langfuse (alternative): [langfuse.com](https://langfuse.com)
- Arcjet (alternative): [arcjet.com](https://arcjet.com)
