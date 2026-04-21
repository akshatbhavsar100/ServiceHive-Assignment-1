# AutoStream – Social-to-Lead AI Agent : By- Akshat Bhavsar

> A LangGraph-powered conversational AI agent that converts social media conversations into qualified business leads for AutoStream, an AI video editing SaaS.

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone <your-repo-url>
cd autostream-agent
pip install -r requirements.txt
```

### 2. Set Up API Key

Get a **free** Google Gemini API key at [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) (no credit card needed).

```bash
# Copy the example environment file
copy .env.example .env

# Edit .env and add your key:
# GOOGLE_API_KEY=AIzaSyCw_p6KB1lqa2TO7UbIUamvunSH4YIFmsA
```

### 3. Run the Agent

**Option A: Using Python directly**
```bash
py main.py
```

**Option B: Using the batch file (Windows)**
```bash
# Double-click run_agent.bat or run from command line:
run_agent.bat
```

### 4. Run Tests (no API key needed)

```bash
py tests/test_components.py
```

---

## 🧪 Example Conversation

```
You: Hi, tell me about your pricing.
  [Product/Pricing Inquiry]
Agent: Hi there! We have two plans to choose from:

The Basic Plan is $29/month and includes 10 videos, 720p resolution, 
basic auto-editing, and standard email support.
Our Pro Plan is $79/month and offers unlimited videos, 4K resolution, 
AI-powered captions, advanced auto-editing, priority 24/7 support, 
custom branding, and an analytics dashboard.

Which one sounds like a better fit for you?

You: I want to try the Pro plan for my YouTube channel.
  [High-Intent Lead]
Agent: Great choice! The Pro Plan is fantastic for creators looking 
for advanced features and unlimited videos.
Ready to get started with AutoStream? What's your name?

You: Jane Smith
Agent: Nice to meet you, Jane Smith!
What's the best email address to use for your AutoStream account?

You: jane@example.com
Agent: Thanks, Jane Smith!
And finally, what platform do you primarily create content for?

You: YouTube

==================================================
LEAD CAPTURED SUCCESSFULLY
==================================================
  Name     : Jane Smith
  Email    : jane@example.com
  Platform : YouTube
  Timestamp: 2026-04-22T00:27:25.430398
==================================================

Agent: Wonderful! Your AutoStream Pro account is now being set up 
with those details. You'll receive a confirmation email shortly 
with instructions on how to log in and start creating amazing videos. 
Welcome to AutoStream, Jane Smith!
```

---

## Troubleshooting

### Common Issues & Solutions

**Issue: "Model not found" error**
```
Error calling model 'gemini-1.5-flash' (NOT_FOUND): 404 NOT_FOUND
```
**Solution**: The model names have been updated. The agent now uses `gemini-2.5-flash` which is available in the current API.

**Issue: Different pricing data in terminal vs IDE**
**Solution**: Ensure you're running the agent from the correct directory:
```bash
cd "c:\Users\ASUS\Desktop\autostream-agent gem\autostream-agent"
py main.py
```

**Issue: API key not working**
**Solution**: 
1. Verify your API key is valid at [aistudio.google.com](https://aistudio.google.com)
2. Ensure the `.env` file is in the same directory as `main.py`
3. Check that the API key is formatted correctly: `GOOGLE_API_KEY=AIza...`

**Issue: "pip command not found"**
**Solution**: Use `py -m pip install -r requirements.txt` instead of `pip install`

### Debug Tools

**Test API key and available models:**
```bash
py test_api.py
```

**Check knowledge base loading:**
```bash
py debug_knowledge.py
```

---

## 🏗️ Architecture

### LLM Configuration

The agent uses **Google Gemini 2.5 Flash** via the `langchain-google-genai` integration:
- Model: `gemini-2.5-flash`
- Max tokens: 512
- Free tier available via Google AI Studio

### Why LangGraph?

LangGraph was chosen over AutoGen for this project because it offers **explicit, auditable state management** via a typed `StateGraph`. Each conversation turn produces a deterministic state transition, which is critical for a lead-capture workflow where premature tool execution (calling `mock_lead_capture` before all 3 fields are collected) would be a business failure.

AutoGen's multi-agent conversation model is powerful but introduces non-determinism — agents negotiate their roles at runtime, which makes it harder to guarantee the strict sequential `name → email → platform` collection flow required here.

### How State is Managed

The agent uses LangGraph's `StateGraph` with a custom `AgentState` TypedDict:

```
AgentState {
  messages      : full conversation history (Annotated with add_messages reducer)
  intent        : classified intent of the latest user message
  stage         : workflow stage (collecting_name | collecting_email | collecting_platform | done)
  lead_name     : captured lead name
  lead_email    : captured lead email
  lead_platform : captured creator platform
  lead_captured : boolean flag — prevents double-capture
  rag_context   : last retrieved knowledge snippet
}
```

State persists across all 5–6 turns in a session. The `stage` field acts as a guard — once lead qualification begins, the routing logic ignores intent classification and routes directly to `continue_lead_collection`, preventing the agent from being distracted mid-collection.

### Graph Flow

```
START
  │
  ▼
classify_intent
  │
  ├─── greeting ──────────────────→ greet → END
  │
  ├─── product_inquiry ───────────→ retrieve_and_respond (RAG) → END
  │
  ├─── high_intent_lead ──────────→ start_lead_qualification → END
  │                                   (sets stage = collecting_name)
  │
  └─── stage = collecting_* ──────→ continue_lead_collection
                                      │
                                      ├── collecting_name  → ask for email
                                      ├── collecting_email → validate → ask for platform
                                      └── collecting_platform → mock_lead_capture() → END
```

### RAG Pipeline

The RAG pipeline uses **keyword-overlap scoring** over a local `knowledge_base.json` (no vector DB required). The knowledge base is flattened into searchable chunks at query time, scored against the user's message terms, and the top-3 chunks are injected into the LLM system prompt as context. This approach:
- Keeps the project dependency-free from heavy ML libraries
- Works offline (no embedding API calls)
- Is fully deterministic and easy to debug

---

## 📁 Project Structure

```
autostream-agent/
├── main.py                    # CLI entrypoint
├── requirements.txt
├── .env.example
├── data/
│   └── knowledge_base.json    # Local RAG knowledge base (pricing, policies, FAQs)
├── agent/
│   ├── graph.py               # LangGraph state machine & nodes
│   ├── intent.py              # Intent classification (greeting / inquiry / high-intent)
│   └── rag.py                 # RAG retrieval pipeline
├── tools/
│   └── lead_capture.py        # mock_lead_capture() + validation helpers
└── tests/
    └── test_components.py     # Unit tests (no API key needed)
```

---

## 💬 WhatsApp Deployment via Webhooks

To deploy this agent on WhatsApp, the following architecture would be used:

### Overview

```
WhatsApp User
     │  (sends message)
     ▼
WhatsApp Business API (Meta)
     │  (HTTP POST webhook)
     ▼
FastAPI / Flask Server  ←── Hosted on AWS/GCP/Railway
     │
     ├── Verify webhook signature (X-Hub-Signature-256)
     ├── Extract sender phone number + message text
     ├── Load session state from Redis (keyed by phone number)
     ├── Run autostream_graph.invoke(state)
     ├── Save updated state back to Redis
     └── POST reply to WhatsApp Send Message API
```

### Step-by-Step Integration

1. **Register a WhatsApp Business App** on [Meta for Developers](https://developers.facebook.com).

2. **Set up a webhook endpoint** (e.g., `POST /webhook`) using FastAPI:

```python
from fastapi import FastAPI, Request
import redis, json

app = FastAPI()
r = redis.Redis()

@app.post("/webhook")
async def handle_whatsapp(request: Request):
    body = await request.json()
    message = body["entry"][0]["changes"][0]["value"]["messages"][0]
    phone = message["from"]
    text = message["text"]["body"]

    # Load per-user session state
    raw = r.get(f"session:{phone}")
    state = json.loads(raw) if raw else initial_state()

    # Run agent
    state["messages"].append(HumanMessage(content=text))
    result = autostream_graph.invoke(state)

    # Save state
    r.set(f"session:{phone}", json.dumps(result), ex=3600)

    # Send reply via WhatsApp API
    reply = get_last_ai_message(result)
    send_whatsapp_message(phone, reply)
    return {"status": "ok"}
```

3. **State persistence**: Use Redis (or DynamoDB) with the user's phone number as the session key. Set a TTL (e.g., 1 hour) to auto-expire idle sessions.

4. **Verify webhook**: Meta requires a `GET /webhook` endpoint that validates a `hub.verify_token` challenge during webhook registration.

5. **Message delivery**: Use Meta's Graph API (`POST /{phone_number_id}/messages`) to send replies back to the user.

This architecture supports horizontal scaling — multiple server instances share the same Redis store, so any instance can serve any user's session.

---

## ✅ Evaluation Checklist

| Criterion | Implementation |
|---|---|
| Agent reasoning & intent detection | Rule-based + LLM classification in `agent/intent.py` |
| Correct use of RAG | Keyword-scored retrieval in `agent/rag.py` |
| Clean state management | LangGraph `StateGraph` with `AgentState` TypedDict |
| Proper tool calling logic | `mock_lead_capture()` only fires after all 3 fields collected |
| Code clarity & structure | Modular packages: `agent/`, `tools/`, `data/`, `tests/` |
| Real-world deployability | WhatsApp webhook architecture documented above |
| LLM used | Gemini 2.5 Flash (free tier via Google AI Studio) |
