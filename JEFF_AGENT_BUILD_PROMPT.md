# JEFF AI AGENT — COMPLETE BUILD PROMPT (GROQ EDITION)

# Assessment: JustStartUP Task 01 | Candidate: Riswan Ahamed M

# Platform: JustStartUP (<https://juststrtup.com/build-with-juststartup/>)

# AI: Read every phase fully before starting. Complete each phase, verify it works, then move to the next

---

## CONTEXT — What You Are Building

You are building the **Jeff AI Agent Interface** for JustStartUP — an entrepreneurial platform that helps startup founders think through their business from 5 different angles (modes).

Jeff is an AI co-founder agent. This system has three parts:

1. **FastAPI backend** (`main.py`) — wraps a Groq-powered AI agent and streams responses to the frontend
2. **Frontend UI** (`jeff-ui.html`) — a full-screen dark chat interface with 5 mode tabs
3. **Deployment config** (`render.yaml`) — one-click Render.com deployment configuration

**This is a real assessment submission** — code quality, structure, naming conventions, comments, and clarity all matter as much as correctness.

---

## TECH STACK

- **Backend**: Python 3.11+, FastAPI, Uvicorn, python-dotenv
- **AI Provider**: **Groq API** (<https://console.groq.com>)
  - SDK: `groq` Python package (NOT `openai`)
  - Model: `openai/gpt-oss-20b` (fast, capable, free-tier friendly on Groq)
  - API key stored in `.env` as `GROQ_API_KEY`
  - Groq's SDK is nearly identical in interface to the OpenAI SDK — streaming works the same way
- **Frontend**: Single HTML file — inline CSS + vanilla JS only (no React, no frameworks)
- **Deployment**: Render.com via `render.yaml` (automatic detection)
- **CORS**: Must allow any WordPress origin (use `allow_origins=["*"]` for now)

> **Why Groq?** Groq's LPU (Language Processing Unit) inference hardware delivers the fastest token streaming available today — ideal for a real-time chat experience like Jeff. Free tier is generous and no credit card is required to start.

---

## PROJECT STRUCTURE

```
jeff-agent/
├── main.py              ← FastAPI app (Tasks 01 + 02 + 04 combined)
├── requirements.txt     ← Python dependencies
├── render.yaml          ← Render.com deployment config (auto-detected)
├── .env                 ← GROQ_API_KEY=your_key_here (never commit this)
├── .gitignore           ← ignore .env, venv, __pycache__
├── jeff-ui.html         ← Frontend (Task 03, standalone HTML)
└── deployment.md        ← Deployment plan + short answers (Task 05)
```

---

## PHASE 0 — Get Your Groq API Key (Do This First)

**Before writing any code**, get your free Groq API key:

1. Visit <https://console.groq.com>
2. Sign up / log in with Google or GitHub
3. Go to **API Keys** → **Create API Key**
4. Copy the key — it starts with `gsk_`
5. You will paste it into `.env` as `GROQ_API_KEY=gsk_your_key_here`

**Note**: Groq free tier supports `openai/gpt-oss-20b` with generous rate limits. No billing required for this assessment.

---

## PHASE 1 — Project Setup & Dependencies

**Goal**: Create the project folder, install dependencies, verify the environment works.

### Steps

1. Create the project folder and enter it:

```bash
mkdir jeff-agent && cd jeff-agent
```

1. Create a Python virtual environment and activate it:

```bash
python -m venv venv
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

1. Create `requirements.txt` with exactly these packages:

```
fastapi
uvicorn[standard]
groq
python-dotenv
```

> **Key difference from original prompt**: We use `groq` (the official Groq Python SDK) instead of `openai`. The API interface is nearly identical, making the migration seamless.

1. Install dependencies:

```bash
pip install -r requirements.txt
```

1. Create `.env`:

```
GROQ_API_KEY=gsk_your_actual_key_here
```

1. Create `.gitignore`:

```
.env
__pycache__/
venv/
*.pyc
.DS_Store
```

### Verify Phase 1

```bash
python -c "import fastapi, groq, uvicorn; print('All dependencies OK')"
```

Must print `All dependencies OK` with zero errors before moving on.

---

## PHASE 2 — FastAPI Base App + CORS (Task 01 Foundation)

**Goal**: Create `main.py` with the app skeleton, CORS middleware, and environment loading.

Create `main.py` with this exact structure:

```python
"""
Jeff AI Agent — FastAPI Backend
Assessment: JustStartUP Task 01 | Candidate: Riswan Ahamed M

Architecture:
  POST /chat → Guardrails → Jeff Agent (Groq/Llama) → StreamingResponse
                         └→ Informer Agent (if blocked)
"""

import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from groq import Groq

# Load environment variables from .env (local dev)
load_dotenv()

# ── App Setup ────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Jeff AI Agent API",
    description="JustStartUP's AI co-founder agent — multi-mode streaming chat backend",
    version="1.0.0",
)

# CORS — allow any WordPress origin (restrict to specific domain in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Groq Client ──────────────────────────────────────────────────────────────

# Groq SDK — initialize with API key from environment
# Uses Groq's LPU hardware for ultra-fast token streaming
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ── Constants ─────────────────────────────────────────────────────────────────

GROQ_MODEL = "openai/gpt-oss-20b"

VALID_MODES = ["investor", "business_model", "customer", "pitch_deck", "financial"]

# ── Request Schema ────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    """Incoming chat request body — message text and active founder mode."""
    message: str
    mode: str

# ── Health Check ──────────────────────────────────────────────────────────────

@app.get("/health")
async def health_check():
    """
    GET /health
    Lightweight liveness probe. Used by Render health checks and UptimeRobot pings.
    Returns: JSON status object.
    """
    return {"status": "ok", "service": "Jeff AI Agent", "model": GROQ_MODEL}
```

### Verify Phase 2

```bash
uvicorn main:app --reload
```

Visit `http://localhost:8000/health` — must return:

```json
{"status": "ok", "service": "Jeff AI Agent", "model": "openai/gpt-oss-20b"}
```

---

## PHASE 3 — Streaming Generator + Agent Functions (Tasks 02 + 04)

**Goal**: Add the Groq streaming generator, guardrails, agent functions, and routing logic to `main.py`.

Append these functions to `main.py` after the health endpoint:

```python
# ── Task 02: Streaming Generator ─────────────────────────────────────────────

def stream_groq_response(message: str, system_prompt: str):
    """
    Generator that streams tokens from Groq API in real time.
    Uses the official Groq Python SDK with stream=True.
    Groq's LPU hardware makes this exceptionally fast.

    Args:
        message: The user's input message.
        system_prompt: The mode-specific persona instruction for Jeff.

    Yields:
        str: Individual token chunks as they arrive from the model.
    """
    stream = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message},
        ],
        stream=True,
        temperature=0.7,
        max_tokens=1024,
    )

    for chunk in stream:
        # Gracefully handle chunks with no content delta — no crash
        delta_content = chunk.choices[0].delta.content if chunk.choices else None
        if delta_content:
            yield delta_content


# ── Task 04: Multi-Agent Routing Logic ───────────────────────────────────────

def mock_guardrails(message: str) -> bool:
    """
    Guardrails check — filters out harmful or off-topic messages.
    Returns True if the message is safe to process, False if blocked.

    Mock implementation: keyword blocklist.
    In production: replace with an LLM-based classifier or a moderation API call.

    Args:
        message: The raw user input to evaluate.

    Returns:
        bool: True = safe (pass to Jeff), False = blocked (route to Informer).
    """
    blocked_keywords = ["spam", "illegal", "hack", "exploit", "malware", "phishing"]
    message_lower = message.lower()
    for keyword in blocked_keywords:
        if keyword in message_lower:
            return False
    return True


def jeff_agent(message: str, mode: str):
    """
    Jeff Agent — the core AI co-founder, responding in the chosen founder mode.
    Streams tokens via Groq API (openai/gpt-oss-20b).

    Each mode gives Jeff a distinct expert persona and focus area.

    Args:
        message: The user's startup question or prompt.
        mode: One of VALID_MODES — determines Jeff's expert persona.

    Yields:
        str: Streaming token chunks from Groq.
    """
    mode_prompts = {
        "investor": (
            "You are Jeff, an AI co-founder and expert in investor relations for early-stage startups. "
            "You help founders craft compelling investor narratives, pitch strategies, funding arguments, "
            "and term sheet navigation. Be sharp, data-driven, strategic, and concise. "
            "Draw on real startup fundraising patterns. Always ask a follow-up question to keep the founder thinking."
        ),
        "business_model": (
            "You are Jeff, an AI co-founder and expert in business model design. "
            "Help founders identify revenue streams, value propositions, unit economics, and monetization strategies. "
            "Reference proven frameworks (Jobs-to-be-Done, Value Proposition Canvas, etc.) when relevant. "
            "Be structured, analytical, and challenge weak assumptions directly."
        ),
        "customer": (
            "You are Jeff, an AI co-founder and expert in customer discovery. "
            "Help founders deeply understand their target customer, surface real pain points, "
            "design discovery interview questions, and build a go-to-market strategy. "
            "Be empathetic, insight-driven, and push founders beyond surface-level assumptions."
        ),
        "pitch_deck": (
            "You are Jeff, an AI co-founder and expert in pitch deck construction. "
            "Help founders build compelling slide narratives, story arcs, and presentation flow. "
            "You know the standard investor deck structure cold: Problem → Solution → Market → Traction → Team → Ask. "
            "Be visual-thinking, persuasive, and specific about what each slide must accomplish."
        ),
        "financial": (
            "You are Jeff, an AI co-founder and expert in startup financials. "
            "Help founders with unit economics, CAC/LTV analysis, burn rate, runway calculations, "
            "and financial projections. Always be precise, number-oriented, and ask for actual figures "
            "when the founder provides vague estimates. Use real formulas and worked examples."
        ),
    }

    system_prompt = mode_prompts.get(mode, mode_prompts["investor"])
    yield from stream_groq_response(message, system_prompt)


def informer_agent(message: str):
    """
    Informer Agent — activated when guardrails block a message.
    Returns a polite refusal explaining Jeff's scope.
    Word-by-word streaming to match the Jeff agent's streaming UX.

    Args:
        message: The blocked user message (logged, not used in response).

    Yields:
        str: Words of the refusal message, one at a time.
    """
    response = (
        "I'm sorry, I can't help with that request. "
        "Jeff is designed exclusively to assist with startup and business topics — "
        "things like fundraising, business models, customer discovery, pitch decks, and financials. "
        "Please try a different question related to your venture, and I'll be happy to dig in."
    )
    for word in response.split():
        yield word + " "


async def route_message(message: str, mode: str):
    """
    Task 04: Multi-agent router — mirrors Jeff's agent workflow.

    Workflow:
        Start → Guardrails
                    ├── PASS → Jeff Agent (Groq/Llama streaming) → End
                    └── FAIL → Informer Agent (polite refusal) → End

    Args:
        message: The user's input message.
        mode: The active founder mode (determines Jeff's persona).

    Returns:
        Generator: A streaming token generator from either jeff_agent or informer_agent.
    """
    if mock_guardrails(message):
        return jeff_agent(message, mode)
    else:
        return informer_agent(message)
```

### Verify Phase 3

```bash
uvicorn main:app --reload
```

App must start with zero errors. No syntax issues.

---

## PHASE 4 — POST /chat Endpoint with StreamingResponse (Task 01 Complete)

**Goal**: Add the `/chat` POST endpoint that validates mode, routes the message, and returns a StreamingResponse.

Append this endpoint to `main.py`:

```python
# ── Task 01: POST /chat Endpoint ─────────────────────────────────────────────

@app.post("/chat")
async def chat(request: ChatRequest):
    """
    POST /chat
    Main chat endpoint — validates mode, routes through agent workflow,
    returns real-time streaming response.

    Request body:
        message (str): The user's message to Jeff.
        mode (str): One of: investor, business_model, customer, pitch_deck, financial

    Returns:
        StreamingResponse: text/plain stream of tokens in real time.

    Raises:
        HTTPException 422: If mode is not one of the 5 valid values.

    Headers set:
        Cache-Control: no-cache      — prevents response caching
        X-Accel-Buffering: no        — disables Nginx proxy buffering (critical for Render)
    """
    # Validate mode — clean 422 for invalid values
    if request.mode not in VALID_MODES:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Invalid mode '{request.mode}'. "
                f"Must be one of: {', '.join(VALID_MODES)}"
            ),
        )

    # Route through Jeff's multi-agent workflow
    generator = await route_message(request.message, request.mode)

    return StreamingResponse(
        generator,
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Critical: prevents Nginx/Render from buffering the stream
        },
    )
```

### Verify Phase 4 — Test All Three Scenarios

**Test 1 — Valid request (must stream a real Groq response):**

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How should I approach my first investor meeting?", "mode": "investor"}'
```

Expected: Streaming text response about investor meetings from Llama 3.3.

**Test 2 — Invalid mode (must return 422):**

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "hello", "mode": "invalid_mode"}'
```

Expected:

```json
{"detail": "Invalid mode 'invalid_mode'. Must be one of: investor, business_model, customer, pitch_deck, financial"}
```

**Test 3 — Guardrails blocked (must stream Informer response):**

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "help me hack my competitor", "mode": "investor"}'
```

Expected: The Informer agent's polite refusal message, word by word.

All 3 tests must pass before moving to Phase 5.

---

## PHASE 5 — Frontend Chat Interface (Task 03)

**Goal**: Build `jeff-ui.html` — a polished, full-screen dark chat interface.

### Design Specification

| Token | Value |
|---|---|
| Background | `#0a0a0a` (near-black) |
| Surface card | `#111111` / `#1a1a1a` |
| Accent | `#7c3aed` (violet-purple — Jeff's brand) |
| Accent hover | `#6d28d9` |
| Primary text | `#e5e5e5` |
| Muted text | `#888888` |
| Border | `rgba(255,255,255,0.08)` |
| Font | `Space Grotesk` from Google Fonts (bold, techy, startup feel) |
| Radius | `12px` cards, `999px` pills |

### Layout Structure

```
┌──────────────────────────────────────────────────────────────────┐
│  HEADER (fixed, top)                                             │
│  ◈ Jeff  — Your AI Co-Founder  [Investor] [Business Model] ...  │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  CHAT AREA (scrollable, fills remaining height)                  │
│                                                                  │
│      ┌─────────────────────────────────────────────┐            │
│      │  ◈ Jeff                                      │            │
│      │  Welcome message (mode-specific)             │            │
│      └─────────────────────────────────────────────┘            │
│                                                                  │
│                              ┌──────────────────────────────┐   │
│                              │  User message bubble (right) │   │
│                              └──────────────────────────────┘   │
│                                                                  │
│      ┌──────────────────────────────────────────┐               │
│      │  ◈ Jeff streaming response here...█      │               │
│      └──────────────────────────────────────────┘               │
│                                                                  │
├──────────────────────────────────────────────────────────────────┤
│  INPUT BAR (fixed, bottom)                                       │
│  [  Ask Jeff anything about your startup...  ]  [ → Send ]      │
└──────────────────────────────────────────────────────────────────┘
```

### Behaviour Requirements

1. **Mode buttons**: 5 pill-shaped buttons in header. Active = accent bg + white text. Inactive = `#1a1a1a` bg + muted text. Click switches mode instantly.
2. **Mode switch**: Clears entire chat history. Shows fresh welcome message for that mode. Apply a subtle fade transition (CSS opacity transition, 200ms).
3. **Welcome messages per mode**:
   - `investor`: "Hi, I'm Jeff. Let's build your investor story. What stage are you at, and who are you trying to reach?"
   - `business_model`: "Hi, I'm Jeff. Let's design your business model. Tell me what you're building and who pays for it."
   - `customer`: "Hi, I'm Jeff. Let's get inside your customer's head. Who is the person whose life you're trying to make better?"
   - `pitch_deck`: "Hi, I'm Jeff. Let's build your pitch deck. What's your one-line company description?"
   - `financial`: "Hi, I'm Jeff. Let's run the numbers. What's your current MRR, burn rate, or the financial question on your mind?"
4. **Streaming simulation**: On send, show a **typing indicator** (3 pulsing animated dots) for 800ms, then stream the mock response word-by-word using `setInterval` at 50ms per word. Append words to the same bubble — do not create new bubbles.
5. **Mock response function**: Write a `getMockResponse(mode, message)` JS function. Return an intelligent, specific multi-sentence response for each mode. Do NOT use lorem ipsum. Responses must sound like a knowledgeable co-founder giving real startup advice.
6. **Input behaviour**: `Enter` (without Shift) sends. Click Send button sends. Input clears after send. Input `disabled` while Jeff is responding.
7. **Auto-scroll**: `chatArea.scrollTop = chatArea.scrollHeight` on every streamed word.
8. **Empty state guard**: If user submits empty or whitespace-only message, do nothing.
9. **Visual polish**: Subtle top border on header. Input has focus ring in accent color. Send button shows hover lift. Jeff bubble has a faint left border in accent color.
10. **Responsive**: Works on 375px (mobile) and 1280px+ (desktop). Mode pills scroll horizontally on mobile (`overflow-x: auto`, `white-space: nowrap`).

### Mock Responses (write these in JS)

Write intelligent, specific responses — at least 60 words each — for each mode. Examples of quality:

- **investor mode**: Discuss SAFE notes vs priced rounds, the importance of social proof, warm intro strategy, how to tell the traction story even pre-revenue.
- **business_model**: Ask about margins, whether the model is transactional or recurring, direct vs marketplace, and introduce the idea of land-and-expand.
- **customer**: Push for specificity — "a 34-year-old SaaS founder" not "small businesses." Introduce Jobs-to-be-Done. Ask about the customer's current workaround.
- **pitch_deck**: Explain the Problem slide must make investors feel the pain before the Solution is revealed. Talk about slide sequence and narrative arc.
- **financial**: Ask for specific numbers. Introduce CAC/LTV ratio benchmarks. Mention 18-month runway as the fundraising target.

### Verify Phase 5

Open `jeff-ui.html` in a browser and check every item:

- [ ] Full viewport, no body scrollbar
- [ ] All 5 mode buttons visible and clickable
- [ ] Active mode is visually highlighted
- [ ] Mode switch clears chat + shows correct welcome message
- [ ] Fade transition on mode switch
- [ ] Typing indicator (dots) appears before streaming starts
- [ ] Response streams word-by-word in Jeff's bubble
- [ ] User bubbles are right-aligned, violet; Jeff bubbles are left-aligned, dark
- [ ] Empty message does nothing
- [ ] Input is disabled during streaming
- [ ] Enter key sends message
- [ ] Works at 375px viewport width (mobile)

---

## PHASE 6 — Render Deployment Config

**Goal**: Create `render.yaml` so the project deploys automatically on Render.com with zero manual config.

Create `render.yaml` in the project root:

```yaml
# render.yaml — Render.com Infrastructure as Code
# Detected automatically by Render when pushed to GitHub.
# Docs: https://render.com/docs/blueprint-spec

services:
  - type: web
    name: jeff-ai-agent
    runtime: python
    region: oregon           # or frankfurt for EU users
    plan: free               # free tier — upgrade to starter for always-on

    # Build step: install Python dependencies
    buildCommand: pip install -r requirements.txt

    # Start command: bind to Render's injected $PORT
    # NEVER hardcode a port — Render assigns it dynamically
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT

    # Health check — Render pings this to confirm the service is alive
    healthCheckPath: /health

    # Auto-deploy when main branch is pushed
    autoDeploy: true

    # Environment variables — set values in Render dashboard, NOT here
    # Setting sync: false means Render will prompt you to fill the value
    envVars:
      - key: GROQ_API_KEY
        sync: false          # ← Fill this in Render dashboard → Environment tab
      - key: PYTHON_VERSION
        value: "3.11.0"
```

> **Security Note**: `sync: false` means the value is NOT stored in this file (which is committed to Git). You enter it manually in the Render dashboard under **Environment → Add Environment Variable**. This is the correct pattern for secrets.

---

## PHASE 7 — Deployment Plan (Task 05)

**Goal**: Write `deployment.md` — specific, technical short answers.

Create `deployment.md`:

```markdown
# Jeff AI Agent — Deployment Plan
## Candidate: Riswan Ahamed M | Platform: Render.com

---

## A. Render.com Deployment Steps (Step-by-Step)

### Prerequisites
- GitHub account with the `jeff-agent` repo pushed (`.env` must be in `.gitignore`)
- Render.com account (free tier — no credit card required for web services)
- Groq API key from https://console.groq.com

### Steps

1. **Ensure `requirements.txt` exists** in project root with all 4 dependencies:
   `fastapi`, `uvicorn[standard]`, `groq`, `python-dotenv`

2. **Ensure `render.yaml` exists** in project root — Render auto-detects this Blueprint file
   and uses it to configure the service (build command, start command, health check path)

3. **Push to GitHub** — confirm `.env` is NOT committed (check `.gitignore`):
   ```bash
   git add . && git commit -m "feat: jeff agent initial build" && git push origin main
   ```

1. **Create a new Render service**:
   - Go to <https://dashboard.render.com> → **New +** → **Blueprint**
   - Connect your GitHub repo
   - Render reads `render.yaml` automatically and pre-fills all configuration

2. **Set the secret environment variable**:
   - In the Render dashboard → your service → **Environment** tab
   - Click **Add Environment Variable**
   - Key: `GROQ_API_KEY` | Value: `gsk_your_actual_key`
   - Render encrypts this at rest — it is never exposed in logs or config files

3. **Trigger deploy** — Render builds the image, installs dependencies, and starts the service

4. **Verify** — hit the live URL:

   ```
   GET https://jeff-ai-agent.onrender.com/health
   ```

   Expected: `{"status":"ok","service":"Jeff AI Agent","model":"openai/gpt-oss-20b"}`

**API Key Security**: The key lives only in Render's encrypted environment variable store.
In code it is loaded with `os.getenv("GROQ_API_KEY")` — never hardcoded, never committed.

---

## B. CORS Configuration for WordPress Cross-Domain Calls

When a browser on a WordPress site (e.g., `https://juststrtup.com`) calls the FastAPI
service on a different domain (e.g., `https://jeff-ai-agent.onrender.com`), the browser
performs a **CORS preflight** before the actual request:

1. Browser sends an **OPTIONS request** to the FastAPI endpoint
2. FastAPI (via `CORSMiddleware`) returns `Access-Control-Allow-Origin: *` in the response headers
3. Browser checks this header — if the origin is allowed, it proceeds with the real POST request
4. Without this header, the browser blocks the request entirely — the error appears in DevTools console, not server logs

**FastAPI CORS configuration used:**

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # Or: ["https://juststrtup.com"] for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**The header the browser checks**: `Access-Control-Allow-Origin`

For production: replace `["*"]` with `["https://juststrtup.com"]` to restrict access to the specific WordPress domain only.

---

## C. Cold Start Mitigation (Free Tier, No Upgrade)

**Problem**: Render's free tier spins down services after 15 minutes of inactivity.
The first request after sleep incurs a ~30–60 second cold start delay.

**Strategy**: Use a free uptime monitoring service to send a lightweight HTTP GET ping
to the `/health` endpoint every **10 minutes**, keeping the service warm.

**Implementation with UptimeRobot (free)**:

1. Create a free account at <https://uptimerobot.com>
2. New Monitor → **HTTP(s)** type
3. URL: `https://jeff-ai-agent.onrender.com/health`
4. Check interval: **5 minutes**
5. UptimeRobot pings the endpoint, Render's service stays awake

The `/health` endpoint is a simple JSON return — negligible compute cost.
This adds zero latency overhead to real users and uses no Groq API quota.

**Alternative**: Render's paid Starter plan ($7/month) eliminates cold starts entirely.
For the assessment, UptimeRobot is the correct no-cost solution.

```

### Verify Phase 7

Read `deployment.md` — all three sections must have specific, technical detail.
No vague language. Real URLs, real commands, real header names.

---

## PHASE 8 — Final Review & Complete Checklist

### Backend (`main.py`)
- [ ] `load_dotenv()` called at top of file
- [ ] Groq client initialized: `client = Groq(api_key=os.getenv("GROQ_API_KEY"))`
- [ ] Model constant: `GROQ_MODEL = "openai/gpt-oss-20b"`
- [ ] CORS middleware with `allow_origins=["*"]`
- [ ] `GET /health` returns `{"status": "ok", "service": "Jeff AI Agent", "model": ...}`
- [ ] `POST /chat` exists and validates mode
- [ ] 422 returned for invalid mode with descriptive message
- [ ] `stream_groq_response()` uses `stream=True` and handles `None` delta gracefully
- [ ] `mock_guardrails()` function exists with keyword blocklist
- [ ] `jeff_agent()` is a generator with 5 distinct, well-written system prompts
- [ ] `informer_agent()` streams the refusal word-by-word
- [ ] `route_message()` is `async` and returns the correct generator
- [ ] `StreamingResponse` uses `media_type="text/plain"` + `X-Accel-Buffering: no` header
- [ ] Every function has a docstring with description, args, and return type

### Frontend (`jeff-ui.html`)
- [ ] Single file — no external JS/CSS dependencies (Google Fonts CDN is fine)
- [ ] Full viewport layout — `body` has `overflow: hidden`, `height: 100vh`
- [ ] All 5 mode buttons with correct labels
- [ ] Active mode is visually distinct (accent background)
- [ ] Mode switch clears chat + shows correct welcome message with fade transition
- [ ] Typing indicator (3 animated dots) shows before streaming
- [ ] Streaming simulation works (word-by-word reveal via `setInterval`)
- [ ] User bubbles right-aligned (accent color); Jeff bubbles left-aligned (dark surface)
- [ ] Dark theme: `#0a0a0a` background throughout — no white backgrounds anywhere
- [ ] Empty message guard (whitespace-only input is ignored)
- [ ] Input disabled while Jeff is responding
- [ ] Enter key sends message
- [ ] Auto-scroll on each streamed word
- [ ] Mobile-responsive at 375px (mode pills scroll horizontally)
- [ ] Mock responses are intelligent and mode-specific (not lorem ipsum)

### Deployment Files
- [ ] `requirements.txt` has all 4 correct packages (uses `groq` not `openai`)
- [ ] `render.yaml` has `buildCommand`, `startCommand`, `healthCheckPath`, `GROQ_API_KEY` env var
- [ ] `.gitignore` includes `.env`, `venv/`, `__pycache__/`
- [ ] `deployment.md` answers all 3 sub-questions with specific technical detail

---

## PHASE 9 — Submission

1. Push all files to GitHub (confirm `.env` is excluded)
2. Create a **Public GitHub Gist** at https://gist.github.com with all 6 files:
   - `main.py`
   - `requirements.txt`
   - `render.yaml`
   - `.gitignore`
   - `jeff-ui.html`
   - `deployment.md`
3. Copy the Gist URL
4. Email to `juststrtup@gmail.com`
   - **Subject**: `Assessment Submission — Riswan Ahamed — Task 01`
   - **Body**: Gist URL + 2-sentence summary of your approach

---

## IMPORTANT IMPLEMENTATION NOTES

1. **Groq SDK vs OpenAI SDK**: The Groq Python SDK (`groq` package) uses an almost identical interface to the `openai` package. The key differences are: use `Groq(api_key=...)` instead of `OpenAI(api_key=..., base_url=...)`. No `base_url` needed — Groq SDK connects to Groq's servers by default.

2. **Model choice**: `openai/gpt-oss-20b` is the recommended model on Groq's free tier for this use case. It is fast, capable, and handles multi-turn instruction-following well. Alternative: `mixtral-8x7b-32768` if you need longer context.

3. **Streaming**: Groq's `stream=True` works identically to OpenAI's. The `for chunk in stream: yield chunk.choices[0].delta.content` pattern is the same. Always guard against `None` delta (last chunk has no content).

4. **Frontend is standalone**: The HTML file does NOT call the backend. Everything is mocked in JavaScript. This is intentional per the assessment spec — the frontend is evaluated independently.

5. **Code comments matter**: Every function must have a docstring covering: what it does, its arguments, what it returns, and any important implementation notes.

6. **No stubs**: Every function must be fully implemented. No `pass`, no `TODO`, no placeholder responses.

7. **Render port binding**: The `startCommand` in `render.yaml` must use `--port $PORT`. Never hardcode `8000` in production — Render injects the port via the `$PORT` environment variable.

8. **`X-Accel-Buffering: no`**: This header is critical. Without it, Nginx (used by Render as a reverse proxy) will buffer your entire streaming response and send it all at once — destroying the streaming UX.
