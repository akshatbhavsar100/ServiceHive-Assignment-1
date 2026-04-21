"""
agent/graph.py
LangGraph-based agentic workflow for AutoStream Social-to-Lead agent.

State machine:
  START → classify_intent → [greet | retrieve_knowledge | qualify_lead] → END

Lead qualification sub-flow:
  qualify_lead → collect_name → collect_email → collect_platform → capture_lead → END
"""

from typing import TypedDict, Annotated, Optional
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from agent.intent import classify_intent, INTENT_GREETING, INTENT_PRODUCT_INQUIRY, INTENT_HIGH_INTENT_LEAD
from agent.rag import retrieve
from tools.lead_capture import mock_lead_capture, validate_email


# ─────────────────────────────────────────────
# STATE
# ─────────────────────────────────────────────

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]   # Full conversation history
    intent: str                                # Classified intent of last user msg
    stage: str                                 # Workflow stage for lead collection
    lead_name: Optional[str]
    lead_email: Optional[str]
    lead_platform: Optional[str]
    lead_captured: bool
    rag_context: Optional[str]                 # Retrieved knowledge for current turn


# ─────────────────────────────────────────────
# LLM
# ─────────────────────────────────────────────

llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", max_tokens=512, temperature=0.1)

SYSTEM_PROMPT = """You are Alex, a friendly and knowledgeable sales assistant for AutoStream — an AI-powered video editing SaaS for content creators.

Your goals:
1. Answer product/pricing questions accurately using the provided knowledge context.
2. Detect when users are ready to sign up and smoothly transition to collecting their details.
3. Be warm, concise, and helpful — never pushy.

When answering product questions, use ONLY the information in the [KNOWLEDGE BASE] section provided.
When collecting lead info, ask for ONE field at a time (Name → Email → Platform).
Never ask for all three at once.

Keep responses short (2–4 sentences max) unless the user asks for a detailed explanation.
"""


def _call_llm(state: AgentState, user_prompt: str, extra_context: str = "") -> str:
    """Helper to invoke the LLM with system prompt + conversation history."""
    system = SYSTEM_PROMPT
    if extra_context:
        system += f"\n\n[KNOWLEDGE BASE]\n{extra_context}"

    messages = [SystemMessage(content=system)] + state["messages"]
    response = llm.invoke(messages)
    
    # Handle different response formats
    if hasattr(response, 'content'):
        if isinstance(response.content, list):
            # Extract text from structured response
            for item in response.content:
                if isinstance(item, dict) and 'text' in item:
                    return item['text']
        elif isinstance(response.content, str):
            return response.content
    
    # Fallback
    return str(response.content)


# ─────────────────────────────────────────────
# NODES
# ─────────────────────────────────────────────

def node_classify(state: AgentState) -> AgentState:
    """Classify the latest user message intent."""
    last_human = next(
        (m.content for m in reversed(state["messages"]) if isinstance(m, HumanMessage)),
        ""
    )
    intent = classify_intent(last_human, state["messages"])
    return {**state, "intent": intent}


def node_greet(state: AgentState) -> AgentState:
    """Handle casual greetings."""
    response = _call_llm(state, "Greet the user warmly and briefly introduce AutoStream.")
    new_msg = AIMessage(content=response)
    return {**state, "messages": state["messages"] + [new_msg]}


def node_retrieve_and_respond(state: AgentState) -> AgentState:
    """RAG: retrieve relevant knowledge and respond to product/pricing questions."""
    last_human = next(
        (m.content for m in reversed(state["messages"]) if isinstance(m, HumanMessage)),
        ""
    )
    context = retrieve(last_human)
    response = _call_llm(state, last_human, extra_context=context)
    new_msg = AIMessage(content=response)
    return {**state, "messages": state["messages"] + [new_msg], "rag_context": context}


def node_start_lead_qualification(state: AgentState) -> AgentState:
    """User has shown high intent — acknowledge and ask for their name."""
    # Check if we're already mid-collection
    if state.get("stage") in ("collecting_name", "collecting_email", "collecting_platform"):
        return node_continue_lead_collection(state)

    response = (
        "That's awesome — the Pro plan is a great choice for creators! 🎉 "
        "I'd love to get you set up. Could I start with your full name?"
    )
    new_msg = AIMessage(content=response)
    return {**state, "messages": state["messages"] + [new_msg], "stage": "collecting_name"}


def node_continue_lead_collection(state: AgentState) -> AgentState:
    """
    Handle the ongoing lead data collection (name → email → platform).
    Extracts values from the latest human message based on current stage.
    """
    last_human = next(
        (m.content for m in reversed(state["messages"]) if isinstance(m, HumanMessage)),
        ""
    ).strip()

    stage = state.get("stage", "collecting_name")
    updates = {}

    if stage == "collecting_name":
        updates["lead_name"] = last_human
        updates["stage"] = "collecting_email"
        response = f"Nice to meet you, {last_human}! What's your email address?"

    elif stage == "collecting_email":
        if not validate_email(last_human):
            response = "That doesn't look like a valid email. Could you double-check it?"
        else:
            updates["lead_email"] = last_human
            updates["stage"] = "collecting_platform"
            response = "Perfect! And which platform do you primarily create content on? (e.g., YouTube, Instagram, TikTok)"

    elif stage == "collecting_platform":
        updates["lead_platform"] = last_human
        updates["stage"] = "capturing"
        # Trigger lead capture
        result = mock_lead_capture(
            name=state["lead_name"],
            email=state["lead_email"],
            platform=last_human
        )
        updates["lead_captured"] = True
        response = (
            f"You're all set, {state['lead_name']}! 🚀 "
            f"We've captured your details and our team will reach out to your {last_human} account shortly. "
            f"Welcome to AutoStream Pro!"
        )
    else:
        response = "Let me know if you have any other questions!"

    new_msg = AIMessage(content=response)
    return {**state, **updates, "messages": state["messages"] + [new_msg]}


# ─────────────────────────────────────────────
# ROUTING
# ─────────────────────────────────────────────

def route_after_classify(state: AgentState) -> str:
    """Decide which node to run based on intent and current stage."""
    stage = state.get("stage", "")

    # If mid lead collection, continue regardless of intent classification
    if stage in ("collecting_name", "collecting_email", "collecting_platform"):
        return "continue_lead_collection"

    intent = state.get("intent", "")
    if intent == INTENT_GREETING:
        return "greet"
    elif intent == INTENT_HIGH_INTENT_LEAD:
        return "start_lead_qualification"
    else:
        return "retrieve_and_respond"


# ─────────────────────────────────────────────
# GRAPH ASSEMBLY
# ─────────────────────────────────────────────

def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("classify", node_classify)
    graph.add_node("greet", node_greet)
    graph.add_node("retrieve_and_respond", node_retrieve_and_respond)
    graph.add_node("start_lead_qualification", node_start_lead_qualification)
    graph.add_node("continue_lead_collection", node_continue_lead_collection)

    graph.set_entry_point("classify")

    graph.add_conditional_edges(
        "classify",
        route_after_classify,
        {
            "greet": "greet",
            "retrieve_and_respond": "retrieve_and_respond",
            "start_lead_qualification": "start_lead_qualification",
            "continue_lead_collection": "continue_lead_collection",
        }
    )

    graph.add_edge("greet", END)
    graph.add_edge("retrieve_and_respond", END)
    graph.add_edge("start_lead_qualification", END)
    graph.add_edge("continue_lead_collection", END)

    return graph.compile()


# Singleton compiled graph
autostream_graph = build_graph()


def initial_state() -> AgentState:
    """Return a fresh agent state."""
    return AgentState(
        messages=[],
        intent="",
        stage="",
        lead_name=None,
        lead_email=None,
        lead_platform=None,
        lead_captured=False,
        rag_context=None,
    )
