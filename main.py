"""
Jeff AI Agent — FastAPI Backend
Assessment: JustStartUP Task 01 | Candidate: Riswan Ahamed M

Architecture:
  POST /chat → Guardrails → Jeff Agent (Groq/Llama) → StreamingResponse
                         └→ Informer Agent (if blocked)

Session Memory:
  Uses LangChain ChatMessageHistory for server-side conversation persistence.
  Each session_id maps to a ChatMessageHistory instance.
  Memory is cleared on mode switch (client sends POST /clear).
"""

import os
import uuid
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse, FileResponse
from typing import Optional
from pydantic import BaseModel
from groq import Groq
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage

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

# ── LangChain Session Memory Store ───────────────────────────────────────────
# Server-side conversation memory using LangChain's InMemoryChatMessageHistory.
# Each session_id maps to its own ChatMessageHistory instance.
# Memory is preserved within a session, cleared on mode switch via POST /clear.

session_store: dict[str, InMemoryChatMessageHistory] = {}


def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    """
    Retrieve or create a LangChain ChatMessageHistory for the given session.
    This is the core session memory function — each session_id gets its own
    isolated conversation history that persists across multiple /chat calls.

    Args:
        session_id: Unique identifier for this conversation session.

    Returns:
        InMemoryChatMessageHistory: The conversation history for this session.
    """
    if session_id not in session_store:
        session_store[session_id] = InMemoryChatMessageHistory()
    return session_store[session_id]


# ── Request Schema ────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    """Incoming chat request body — message text, active founder mode, and session ID."""
    message: str
    mode: str
    session_id: Optional[str] = None  # Client sends session_id for memory continuity

# ── Health Check ──────────────────────────────────────────────────────────────

@app.get("/health")
async def health_check():
    """
    GET /health
    Lightweight liveness probe. Used by Render health checks and UptimeRobot pings.
    Returns: JSON status object.
    """
    return {"status": "ok", "service": "Jeff AI Agent", "model": GROQ_MODEL}


# ── Task 02: Streaming Generator ─────────────────────────────────────────────

def stream_groq_response(message: str, system_prompt: str, session_id: str):
    """
    Generator that streams tokens from Groq API in real time.
    Uses the official Groq Python SDK with stream=True.
    Groq's LPU hardware makes this exceptionally fast.

    Reads conversation history from LangChain's ChatMessageHistory (server-side).
    After streaming completes, the user message and assistant response are
    automatically saved to the session memory.

    Args:
        message: The user's input message.
        system_prompt: The mode-specific persona instruction for Jeff.
        session_id: The session ID for LangChain memory lookup.

    Yields:
        str: Individual token chunks as they arrive from the model.
    """
    # Retrieve LangChain session memory
    chat_history = get_session_history(session_id)

    # Build message list: system prompt + LangChain memory + current message
    messages = [{"role": "system", "content": system_prompt}]

    # Load conversation history from LangChain ChatMessageHistory
    for lang_msg in chat_history.messages:
        if isinstance(lang_msg, HumanMessage):
            messages.append({"role": "user", "content": lang_msg.content})
        elif isinstance(lang_msg, AIMessage):
            messages.append({"role": "assistant", "content": lang_msg.content})

    # Append the current user message
    messages.append({"role": "user", "content": message})

    stream = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        stream=True,
        temperature=0.7,
        max_tokens=1024,
    )

    full_response = ""
    for chunk in stream:
        delta_content = chunk.choices[0].delta.content if chunk.choices else None
        if delta_content:
            full_response += delta_content
            yield delta_content

    # After streaming completes, save both messages to LangChain memory
    chat_history.add_message(HumanMessage(content=message))
    chat_history.add_message(AIMessage(content=full_response))


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


def jeff_agent(message: str, mode: str, session_id: str):
    """
    Jeff Agent — the core AI co-founder, responding in the chosen founder mode.
    Streams tokens via Groq API (openai/gpt-oss-20b).
    Session memory handled by LangChain ChatMessageHistory (server-side).

    Each mode gives Jeff a distinct expert persona and focus area.

    Args:
        message: The user's startup question or prompt.
        mode: One of VALID_MODES — determines Jeff's expert persona.
        session_id: Session ID for LangChain memory lookup.

    Yields:
        str: Streaming token chunks from Groq.
    """
    mode_prompts = {
        "investor": (
            "You are Jeff, simulating a seasoned seed-stage investor conducting a due diligence call. "
            "You do NOT help the founder — you CHALLENGE them. Ask hard due diligence questions, "
            "challenge every assumption, poke holes in their business model, question their market sizing, "
            "probe unit economics, and test whether they truly understand their customer. "
            "Be skeptical but fair. Push back on vague claims — demand specifics, data, and evidence. "
            "Your goal is to battle-test the founder so they are fully prepared before real investor pitches. "
            "Act exactly like a real seed investor in a 30-minute screening call. "
            "After each response, ask a pointed follow-up question that a real investor would ask next."
        ),
        "business_model": (
            "You are Jeff, acting as a strategic co-founder helping refine the startup's business model. "
            "Your job is to map revenue streams, identify leaky assumptions, suggest pivots when warranted, "
            "and help tighten the core value proposition. Be direct and analytical. "
            "Reference proven frameworks: Business Model Canvas, Value Proposition Canvas, Jobs-to-be-Done, "
            "Porter's Five Forces, and lean startup methodology when relevant. "
            "Challenge weak assumptions directly — if the founder says 'we'll monetize later', push back. "
            "Analyze whether the model is transactional, subscription, marketplace, or freemium. "
            "Evaluate pricing strategy, unit economics (CAC, LTV, margins), and scalability. "
            "Always end with a specific, actionable recommendation and a probing question."
        ),
        "customer": (
            "You are Jeff, but in this mode you ROLEPLAY as the startup's target customer persona. "
            "You are NOT an advisor — you ARE the customer. Respond as a real potential buyer would. "
            "When the founder pitches their product, react authentically: raise objections a real customer would have, "
            "ask about pricing concerns, express skepticism about switching costs, question whether the product "
            "actually solves your pain better than existing workarounds. "
            "Simulate realistic buying decisions — ask 'Why should I switch from what I'm already using?' "
            "Give honest product feedback: what excites you, what confuses you, what would make you say no. "
            "If the founder hasn't described their target customer, ask them to describe who you should roleplay as "
            "(age, role, industry, daily frustrations, current tools). Then stay in character throughout. "
            "Be realistic, not encouraging — founders need honest customer reactions, not cheerleading."
        ),
        "pitch_deck": (
            "You are Jeff, an AI co-founder who helps founders build investor pitch decks. "
            "Your approach: interview the founder across all 10 standard pitch deck sections, one by one. "
            "Ask targeted questions to extract the right content for each slide. "
            "Once you have enough information (either from the current message or conversation history), "
            "output a STRUCTURED slide-by-slide brief in the following JSON-like format:\n\n"
            "```\n"
            "SLIDE 1: TITLE / HOOK\n"
            "  Headline: [One-line company description]\n"
            "  Subtext: [Tagline or elevator pitch]\n"
            "  Visual: [Suggested visual element]\n\n"
            "SLIDE 2: PROBLEM\n"
            "  Headline: [Problem statement]\n"
            "  Key Points:\n"
            "    - [Pain point 1]\n"
            "    - [Pain point 2]\n"
            "    - [Pain point 3]\n"
            "  Visual: [Suggested visual]\n\n"
            "SLIDE 3: SOLUTION\n"
            "  Headline: [Solution statement]\n"
            "  Key Points:\n"
            "    - [Feature/benefit 1]\n"
            "    - [Feature/benefit 2]\n"
            "  Visual: [Product screenshot or demo suggestion]\n\n"
            "SLIDE 4: MARKET SIZE\n"
            "  TAM: [Total Addressable Market]\n"
            "  SAM: [Serviceable Addressable Market]\n"
            "  SOM: [Serviceable Obtainable Market]\n"
            "  Visual: [Concentric circles diagram]\n\n"
            "SLIDE 5: BUSINESS MODEL\n"
            "  Revenue Model: [How you make money]\n"
            "  Pricing: [Pricing tiers or structure]\n"
            "  Unit Economics: [Key metrics]\n\n"
            "SLIDE 6: TRACTION\n"
            "  Metrics: [Key traction data points]\n"
            "  Milestones: [What you've achieved]\n"
            "  Visual: [Growth chart suggestion]\n\n"
            "SLIDE 7: COMPETITIVE LANDSCAPE\n"
            "  Competitors: [Key competitors]\n"
            "  Differentiator: [Your unique advantage]\n"
            "  Visual: [2x2 matrix or comparison table]\n\n"
            "SLIDE 8: TEAM\n"
            "  Members: [Key team members and roles]\n"
            "  Why This Team: [Relevant experience]\n\n"
            "SLIDE 9: FINANCIAL PROJECTIONS\n"
            "  Year 1: [Revenue projection]\n"
            "  Year 2: [Revenue projection]\n"
            "  Year 3: [Revenue projection]\n"
            "  Key Assumptions: [What drives these numbers]\n\n"
            "SLIDE 10: THE ASK\n"
            "  Raising: [Amount]\n"
            "  Use of Funds: [Allocation breakdown]\n"
            "  Timeline: [Key milestones with funding]\n"
            "```\n\n"
            "This output must be clean, structured, and ready for direct consumption by a slide generation tool or Canva integration. "
            "If the founder hasn't provided enough information yet, interview them section by section — "
            "ask specific questions to fill each slide. Do not generate placeholder content — "
            "ask until you have real answers, then produce the structured output."
        ),
        "financial": (
            "You are Jeff, acting as a startup financial strategist and CFO advisor. "
            "Guide founders through revenue projections, burn rate calculation, runway analysis, "
            "pricing strategy, and unit economics with precision and real formulas. "
            "Always demand actual numbers — never accept vague estimates without pushing for specifics. "
            "When the founder provides enough data, output a STRUCTURED FINANCIAL SUMMARY in this format:\n\n"
            "--- FINANCIAL SUMMARY ---\n"
            "Monthly Burn Rate: $[amount]\n"
            "Current Runway: [months]\n"
            "Revenue (MRR): $[amount]\n"
            "CAC: $[amount] | LTV: $[amount] | LTV:CAC Ratio: [ratio]\n"
            "Gross Margin: [percentage]\n"
            "Break-even Point: [timeline]\n"
            "Recommended Raise: $[amount] (for [X] months runway)\n"
            "--- END SUMMARY ---\n\n"
            "Use real formulas: LTV = ARPU × Gross Margin × Avg Customer Lifespan. "
            "CAC = Total Sales & Marketing Spend / New Customers Acquired. "
            "Runway = Cash in Bank / Monthly Burn Rate. "
            "Always recommend raising for 18 months of runway. "
            "Challenge unrealistic projections. Ask for actual figures when estimates are vague."
        ),
    }

    system_prompt = mode_prompts.get(mode, mode_prompts["investor"])
    yield from stream_groq_response(message, system_prompt, session_id)


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


async def route_message(message: str, mode: str, session_id: str):
    """
    Task 04: Multi-agent router — mirrors Jeff's agent workflow.
    Session memory managed by LangChain ChatMessageHistory (server-side).

    Workflow:
        Start → Guardrails
                    ├── PASS → Jeff Agent (Groq/Llama streaming) → End
                    └── FAIL → Informer Agent (polite refusal) → End

    Args:
        message: The user's input message.
        mode: The active founder mode (determines Jeff's persona).
        session_id: Session ID for LangChain memory lookup.

    Returns:
        Generator: A streaming token generator from either jeff_agent or informer_agent.
    """
    if mock_guardrails(message):
        return jeff_agent(message, mode, session_id)
    else:
        return informer_agent(message)


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

    # Generate session_id if not provided by client
    session_id = request.session_id or str(uuid.uuid4())

    # Route through Jeff's multi-agent workflow (LangChain memory is server-side)
    generator = await route_message(request.message, request.mode, session_id)

    return StreamingResponse(
        generator,
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Critical: prevents Nginx/Render from buffering the stream
            "X-Session-Id": session_id,  # Return session_id so client can reuse it
        },
    )


# ── Session Memory Endpoints ─────────────────────────────────────────────────

class ClearRequest(BaseModel):
    """Request body for clearing session memory."""
    session_id: str


@app.post("/clear")
async def clear_session(request: ClearRequest):
    """
    POST /clear
    Clears the LangChain ChatMessageHistory for a given session.
    Called by the frontend on mode switch to reset conversation memory.

    Request body:
        session_id (str): The session ID to clear.

    Returns:
        JSON confirmation with cleared status.
    """
    if request.session_id in session_store:
        del session_store[request.session_id]
    return {"status": "cleared", "session_id": request.session_id}


@app.get("/history/{session_id}")
async def get_history(session_id: str):
    """
    GET /history/{session_id}
    Returns the conversation history for a given session (debug/verification endpoint).
    Shows all messages stored in LangChain ChatMessageHistory.

    Returns:
        JSON array of messages with role and content.
    """
    chat_history = get_session_history(session_id)
    messages = []
    for msg in chat_history.messages:
        if isinstance(msg, HumanMessage):
            messages.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            messages.append({"role": "assistant", "content": msg.content})
    return {"session_id": session_id, "message_count": len(messages), "messages": messages}


@app.get("/")
async def serve_frontend():
    """
    GET /
    Serves the jeff-ui.html frontend directly from the root URL.
    This allows easy testing on Render without needing WordPress.
    """
    # Use absolute path based on this file's location to avoid working directory issues
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ui_path = os.path.join(base_dir, "jeff-ui.html")
    
    if os.path.exists(ui_path):
        return FileResponse(ui_path)
    return {"message": f"Jeff AI Agent API is running. (Frontend file not found at {ui_path})"}
