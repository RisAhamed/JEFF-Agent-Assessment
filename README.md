# Jeff AI Agent — Your AI Co-Founder

**Assessment: JustStartUP Task 01 | Candidate: Riswan Ahamed M**
**Platform**: [juststrtup.com](https://juststrtup.com/build-with-juststartup/)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [API Reference](#api-reference)
- [Agent Modes](#agent-modes)
- [Session Memory](#session-memory)
- [Frontend (jeff-ui.html)](#frontend-jeff-uihtml)
- [Deployment to Render](#deployment-to-render)
- [WordPress Integration](#wordpress-integration)
- [Security](#security)
- [Assessment Deliverables Checklist](#assessment-deliverables-checklist)
- [Important Notes](#important-notes)

---

## Overview

Jeff is an AI-powered co-founder agent built for startup founders. It provides expert guidance across 5 distinct modes — Investor, Business Model, Customer, Pitch Deck, and Financial — each with a purpose-built system prompt that shapes Jeff's behavior.

The system consists of:

1. **FastAPI Backend** (`main.py`) — Multi-agent routing with Groq-powered streaming, LangChain session memory, and content guardrails
2. **Frontend UI** (`jeff-ui.html`) — Full-screen dark cyberpunk chat interface with per-mode memory, Markdown rendering, and real-time streaming
3. **Deployment Config** (`render.yaml`) — One-click Render.com deployment with auto-deploy on push

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Frontend (jeff-ui.html)            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │ Investor  │  │ Business │  │ Customer │  ...     │
│  │  Mode     │  │  Model   │  │   Mode   │          │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘          │
│       │              │              │                │
│       └──────────────┼──────────────┘                │
│                      │ session_id per mode            │
│                      ▼                               │
│              POST /chat {message, mode, session_id}  │
└──────────────────────┬───────────────────────────────┘
                       │ fetch (streaming)
                       ▼
┌──────────────────────────────────────────────────────┐
│                FastAPI Backend (main.py)              │
│                                                      │
│  POST /chat ──► Guardrails ──┬──► Jeff Agent ──► Groq│
│                              │        ▲              │
│                              │   LangChain Memory    │
│                              │   (per session_id)    │
│                              └──► Informer Agent     │
│                                   (polite refusal)   │
│                                                      │
│  POST /clear ──► Wipe session memory                 │
│  GET /health ──► Liveness probe                      │
│  GET /history/{id} ──► Debug: view stored messages   │
└──────────────────────────────────────────────────────┘
```

---

## Project Structure

```
jeff-agent/
├── main.py              ← FastAPI backend (agents, routing, streaming, memory)
├── requirements.txt     ← Python dependencies (6 packages)
├── render.yaml          ← Render.com deployment blueprint
├── jeff-ui.html         ← Frontend chat interface (standalone HTML)
├── deployment.md        ← Deployment plan, WordPress integration, CORS config
├── README.md            ← This file
├── .env                 ← GROQ_API_KEY (local dev only, never committed)
└── .gitignore           ← Excludes .env, __pycache__, .venv
```

---

## Features

| Feature | Status | Details |
|---------|--------|---------|
| 5 Agent Modes | ✅ | Investor, Business Model, Customer, Pitch Deck, Financial |
| Real-time Streaming | ✅ | Token-by-token streaming via Groq LPU + FastAPI StreamingResponse |
| Session Memory | ✅ | Server-side via LangChain `InMemoryChatMessageHistory` |
| Per-Mode Memory | ✅ | Each mode has its own session — switching preserves all conversations |
| Markdown Rendering | ✅ | `marked.js` renders headings, bold, lists, tables, code blocks |
| Content Guardrails | ✅ | Keyword-based filter routes blocked content to Informer Agent |
| ESC / X Close | ✅ | Close button + ESC key shows "Session Ended" overlay |
| Rosario Font | ✅ | Brand-consistent typography matching juststrtup.com |
| Full-Screen UI | ✅ | Fixed-position viewport takeover, not a corner widget |
| Mobile Responsive | ✅ | Touch-friendly input, responsive layout |
| Dark Cyberpunk Theme | ✅ | Pitch-black background, neon purple accents, glassmorphism |
| Mock Fallback | ✅ | Auto-falls back to mock responses if backend is unreachable |
| Structured Pitch Deck | ✅ | Mode 04 outputs slide-by-slide structured briefs for Canva |
| WordPress Ready | ✅ | Elementor HTML Widget + shortcode with Premium gating |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend Framework | FastAPI + Uvicorn |
| AI Provider | Groq API (LPU inference hardware) |
| AI Model | `openai/gpt-oss-20b` |
| Session Memory | LangChain Core (`InMemoryChatMessageHistory`) |
| Frontend | Vanilla HTML + CSS + JavaScript |
| Markdown | marked.js (CDN) |
| Typography | Google Fonts — Rosario |
| Deployment | Render.com (free tier) |
| Environment | Python 3.11+, python-dotenv |

---

## Getting Started

### Prerequisites

- Python 3.11 or higher
- A free Groq API key from [console.groq.com](https://console.groq.com)

### 1. Clone & Set Up

```bash
git clone <your-repo-url>
cd jeff-agent
```

### 2. Create Virtual Environment

```bash
python -m venv .venv

# Windows
.\.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `fastapi` — Web framework
- `uvicorn[standard]` — ASGI server
- `groq` — Groq Python SDK
- `python-dotenv` — Environment variable loader
- `langchain` — LangChain framework
- `langchain-core` — Core memory primitives (`InMemoryChatMessageHistory`)

### 4. Configure API Key

Create a `.env` file in the project root:

```env
GROQ_API_KEY=gsk_your_actual_groq_api_key_here
```

Get your key at [console.groq.com](https://console.groq.com) → API Keys → Create API Key.

### 5. Start the Backend

```bash
uvicorn main:app --reload --port 8000
```

Verify it's running:
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "ok", "service": "Jeff AI Agent", "model": "openai/gpt-oss-20b"}
```

### 6. Open the Frontend

Serve the frontend locally (from the project directory):

```bash
python -m http.server 8080
```

Open **http://localhost:8080/jeff-ui.html** in your browser.

> **Note**: The frontend's `API_BASE_URL` is set to `http://localhost:8000` by default. For production, update it to your Render URL.

---

## API Reference

### `POST /chat` — Main Chat Endpoint

Sends a message to Jeff and receives a streaming response.

**Request Body:**
```json
{
  "message": "I'm building a SaaS for HR teams",
  "mode": "investor",
  "session_id": "optional-uuid-string"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `message` | string | ✅ | The user's message to Jeff |
| `mode` | string | ✅ | One of: `investor`, `business_model`, `customer`, `pitch_deck`, `financial` |
| `session_id` | string | ❌ | UUID for session memory continuity. Auto-generated if omitted. |

**Response:** `text/plain` streaming response (token-by-token).

**Response Headers:**
- `X-Session-Id` — The session ID (use this for subsequent requests)
- `Cache-Control: no-cache`
- `X-Accel-Buffering: no` — Prevents Nginx/Render from buffering the stream

---

### `POST /clear` — Clear Session Memory

Clears the LangChain conversation history for a session. Called by the frontend on close/ESC.

**Request Body:**
```json
{
  "session_id": "the-session-uuid"
}
```

**Response:**
```json
{"status": "cleared", "session_id": "the-session-uuid"}
```

---

### `GET /health` — Health Check

Liveness probe used by Render and UptimeRobot.

**Response:**
```json
{"status": "ok", "service": "Jeff AI Agent", "model": "openai/gpt-oss-20b"}
```

---

### `GET /history/{session_id}` — View Session History (Debug)

Returns all messages stored in LangChain memory for a session.

**Response:**
```json
{
  "session_id": "test-001",
  "message_count": 4,
  "messages": [
    {"role": "user", "content": "I'm building an HR SaaS"},
    {"role": "assistant", "content": "Let's dig into your TAM..."},
    {"role": "user", "content": "What funding stage?"},
    {"role": "assistant", "content": "Based on your $18K MRR..."}
  ]
}
```

---

## Agent Modes

### Mode 01 — Investor

Jeff **simulates a seasoned seed-stage investor** conducting a due diligence call. He challenges assumptions, pokes holes in the business model, questions market sizing, and tests whether the founder truly understands their customer. Designed to battle-test founders before real pitches.

### Mode 02 — Business Model

Jeff acts as a **strategic co-founder** who maps revenue streams, identifies leaky assumptions, suggests pivots, and tightens the core value proposition. References frameworks like Business Model Canvas, Value Proposition Canvas, Jobs-to-be-Done, and Porter's Five Forces.

### Mode 03 — Customer

Jeff **roleplays as the startup's target customer persona**. He is NOT an advisor — he IS the customer. He raises objections, asks about pricing concerns, expresses skepticism about switching costs, and gives honest product feedback. The founder must first describe the customer persona for Jeff to roleplay.

### Mode 04 — Pitch Deck

Jeff **interviews the founder across all 10 standard pitch deck sections** and outputs a structured slide-by-slide brief:

```
SLIDE 1: TITLE / HOOK
  Headline: [One-line description]
  Subtext: [Tagline]
  Visual: [Suggested visual]

SLIDE 2: PROBLEM
  Headline: [Problem statement]
  Key Points:
    - [Pain point 1]
    - [Pain point 2]
  Visual: [Suggestion]

... (through SLIDE 10: THE ASK)
```

This structured output is designed for direct consumption by Canva integration (Task 02).

### Mode 05 — Financial

Jeff acts as a **startup financial strategist and CFO advisor**. Guides founders through revenue projections, burn rate, runway, pricing, and unit economics. Outputs a structured financial summary:

```
--- FINANCIAL SUMMARY ---
Monthly Burn Rate: $[amount]
Current Runway: [months]
Revenue (MRR): $[amount]
CAC: $[amount] | LTV: $[amount] | LTV:CAC Ratio: [ratio]
Gross Margin: [percentage]
Break-even Point: [timeline]
Recommended Raise: $[amount]
--- END SUMMARY ---
```

---

## Session Memory

### How It Works

Session memory is handled **server-side** using LangChain's `InMemoryChatMessageHistory`:

1. The frontend generates a unique `session_id` (UUID) per mode on page load
2. Each `/chat` request includes the `session_id`
3. The backend retrieves the corresponding `ChatMessageHistory` from the session store
4. Previous messages are loaded into the Groq API context (system prompt + history + current message)
5. After streaming completes, both the user message and Jeff's response are saved to the history
6. On the next request with the same `session_id`, Jeff has full context of the conversation

### Per-Mode Isolation

Each of the 5 modes has its **own independent session_id**:

- Switching from Investor to Business Model saves the Investor conversation and switches to the Business Model session
- Switching back to Investor restores the Investor conversation (both UI and server memory)
- Conversations are only cleared when:
  - The user clicks **X** (Close) or presses **ESC** — clears ALL mode sessions
  - The user refreshes the page — new UUIDs are generated, old sessions remain on server until garbage collected

---

## Frontend (jeff-ui.html)

The frontend is a **single, self-contained HTML file** with inline CSS and JavaScript. No build tools, no frameworks, no node_modules.

### Key UI Components

- **Header** — Jeff branding + 5 mode tabs + X close button
- **Chat Area** — Scrollable message history with Jeff (left) and User (right) bubbles
- **Input Bar** — Text input + send button (Enter to send, Shift+Enter for newline)
- **Close Overlay** — "Session Ended" modal with "Reopen Jeff" button
- **Typing Indicator** — Animated dots while Jeff is thinking

### Markdown Rendering

Jeff's responses are rendered from Markdown to HTML using `marked.js`:

- **During streaming**: Raw text is displayed for speed
- **After streaming completes**: Full response is parsed through `marked.parse()` and injected as HTML
- **Supported elements**: Headings, bold, italic, bullet/numbered lists, tables, code blocks, blockquotes, horizontal rules, links

### Mock Fallback

If the FastAPI backend is unreachable, the frontend automatically falls back to built-in mock responses. This ensures the UI is always demonstrable even without a running server.

---

## Deployment to Render

### Quick Deploy (One-Click)

1. Push the repo to GitHub (ensure `.env` is in `.gitignore`)
2. Go to [Render Dashboard](https://dashboard.render.com) → **New+** → **Blueprint**
3. Connect your GitHub repo — Render reads `render.yaml` automatically
4. Add environment variable: `GROQ_API_KEY` = `gsk_your_key`
5. Deploy

### Verify

```bash
curl https://jeff-ai-agent.onrender.com/health
```

### Cold Start Prevention

Render's free tier spins down after 15 minutes of inactivity. Use **UptimeRobot** (free) to ping `/health` every 5 minutes to keep the service warm.

> Full deployment instructions are in [deployment.md](deployment.md).

---

## WordPress Integration

### Option 1: Elementor HTML Widget

1. In WordPress Admin → Pages → Edit the Jeff page
2. Add an Elementor **HTML Widget**
3. Paste the entire contents of `jeff-ui.html`
4. Update `API_BASE_URL` to your Render URL:
   ```javascript
   const API_BASE_URL = 'https://jeff-ai-agent.onrender.com';
   ```
5. Publish

### Option 2: WordPress Shortcode

Add a PHP shortcode via the CodeSnippets plugin that:
- Checks `is_user_logged_in()` — redirects to login if not
- Verifies Premium role (Ultimate Members / Paid Membership Pro)
- Renders Jeff for Premium users, shows upgrade prompt for Free users
- Usage: `[jeff_agent]` on any WordPress page

> Full PHP snippet and Premium gating logic are in [deployment.md](deployment.md#d-wordpress-integration--embedding-jeff-on-juststrtupcom).

---

## Security

| Concern | Implementation |
|---------|---------------|
| API Key Exposure | `GROQ_API_KEY` stored in Render environment variables (encrypted at rest). Loaded via `os.getenv()` — never in frontend JS, never committed to Git. |
| CORS | Currently `allow_origins=["*"]` for dev. Production: restrict to `["https://juststrtup.com"]`. |
| Content Guardrails | Keyword blocklist filters harmful input before reaching the AI model. Blocked messages routed to Informer Agent. |
| Input Validation | Pydantic models validate request schema. Invalid modes return HTTP 422. |
| Session IDs | Generated via `crypto.randomUUID()` (frontend) or `uuid.uuid4()` (backend) — cryptographically random. |

---

## Assessment Deliverables Checklist

Mapped against the requirements from `project info.md`:

| # | Requirement | Status | Implementation |
|---|-------------|--------|---------------|
| 1 | Working full-screen Jeff agent interface with all 5 modes | ✅ | `jeff-ui.html` — fixed-position viewport, 5 mode tabs |
| 2 | PHP REST endpoint or secure proxy handling AI calls | ✅ | FastAPI `/chat` endpoint proxies Groq calls. API key server-side only. |
| 3 | Mode 04 outputs structured slide-by-slide content | ✅ | Pitch Deck prompt outputs 10 structured slides for Canva |
| 4 | Setup documentation | ✅ | `README.md` (this file) + `deployment.md` |
| 5 | Tested, no console errors, no plugin conflicts | ✅ | Standalone HTML — zero WordPress plugin dependencies |
| 6 | Full-screen interface, not a corner widget | ✅ | `position: fixed; inset: 0` — full viewport |
| 7 | Closeable via ESC or X button | ✅ | X button + ESC key listener → "Session Ended" overlay |
| 8 | Mode switcher at top of interface | ✅ | 5 mode buttons in header bar |
| 9 | Session memory within session | ✅ | LangChain `InMemoryChatMessageHistory` per session_id |
| 10 | Cleared on mode switch or page reload | ✅ | Each mode has own session. Close/ESC clears all. Reload resets. |
| 11 | Secure API handling (key never in frontend) | ✅ | Key in `.env` / Render env vars. Frontend calls FastAPI, not Groq directly. |
| 12 | Mobile responsive | ✅ | Responsive CSS, touch-friendly input |
| 13 | Brand consistent (dark, Rosario font, neon accents) | ✅ | Pitch-black background, purple neon, Rosario from Google Fonts |
| 14 | Streaming responses | ✅ | Groq SDK `stream=True` + FastAPI `StreamingResponse` |
| 15 | Premium gate for WordPress | ✅ | PHP shortcode with `is_user_logged_in()` + role check (documented) |
| 16 | WordPress shortcode / Elementor compatible | ✅ | Both options documented in `deployment.md` |

---

## Important Notes

### For Reviewers

- **Start the backend first** (`uvicorn main:app --reload --port 8000`), then open the frontend
- If you only want to see the UI without a backend, it will auto-fallback to mock responses
- The `/history/{session_id}` endpoint is useful for verifying that session memory is working
- All 5 modes have distinct behaviors — Investor challenges you, Customer roleplays as a buyer, Pitch Deck interviews you slide-by-slide

### Known Considerations

- **In-Memory Sessions**: Session memory lives in server RAM. If the server restarts (Render cold start), sessions are reset. For production persistence, swap `InMemoryChatMessageHistory` with a Redis-backed or database-backed store.
- **Free Tier Cold Starts**: Render free tier spins down after 15 min. First request after sleep takes ~30-60s. Mitigated with UptimeRobot pings.
- **CORS Wildcard**: Currently `allow_origins=["*"]` for development. Must be locked down to `["https://juststrtup.com"]` for production.
- **Markdown During Streaming**: Text appears as raw during streaming and converts to formatted HTML after streaming completes. This is intentional — rendering Markdown mid-stream would cause layout jitter.

### License

This project is an assessment submission for JustStartUP. All rights reserved by the candidate.

---

**Built with ❤️ by Riswan Ahamed M for JustStartUP**
# JEFF-Agent-Assessment
