"""
agent/intent.py
Rule-based + LLM-assisted intent classification for AutoStream agent.
Classifies each user message into one of three intent categories.
"""

import re

# Intent categories
INTENT_GREETING = "greeting"
INTENT_PRODUCT_INQUIRY = "product_inquiry"
INTENT_HIGH_INTENT_LEAD = "high_intent_lead"

# Keywords for fast rule-based pre-screening
GREETING_KEYWORDS = [
    r"\bhi\b", r"\bhello\b", r"\bhey\b", r"\bgreetings\b",
    r"\bgood (morning|afternoon|evening)\b", r"\bwhat'?s up\b", r"\bhowdy\b"
]

HIGH_INTENT_KEYWORDS = [
    r"\bsign(ing)? up\b", r"\bsubscribe\b", r"\bbuy\b", r"\bpurchase\b",
    r"\bget started\b", r"\btry (it|the|your|pro|basic)\b",
    r"\bi want (to|the)\b", r"\bi'?m? (ready|interested|in)\b",
    r"\blet'?s? (go|do it|start)\b", r"\bsound(s)? good\b",
    r"\bsign me up\b", r"\bstart (the|a|my)\b", r"\bwhere do i\b",
    r"\bhow (do|can) i (sign|get|buy|start|subscribe)\b"
]

PRODUCT_KEYWORDS = [
    r"\bpric(e|ing)\b", r"\bplan\b", r"\bfeature\b", r"\brefund\b",
    r"\bsupport\b", r"\bresolution\b", r"\bvideo\b", r"\bcaption\b",
    r"\b4k\b", r"\b720p\b", r"\bunlimited\b", r"\bbasic\b", r"\bpro\b",
    r"\bhow (much|does|do)\b", r"\bwhat (is|are|does)\b", r"\btell me\b",
    r"\bexplain\b", r"\bquestion\b", r"\binfo\b", r"\babout\b"
]


def _matches_any(text: str, patterns: list[str]) -> bool:
    text_lower = text.lower()
    return any(re.search(p, text_lower) for p in patterns)


def classify_intent(message: str, conversation_history: list[dict] = None) -> str:
    """
    Classify user intent from a message + optional conversation context.

    Returns one of:
        - "greeting"
        - "product_inquiry"
        - "high_intent_lead"
    """
    msg = message.strip()

    # Very short messages are likely greetings
    if len(msg.split()) <= 3 and _matches_any(msg, GREETING_KEYWORDS):
        return INTENT_GREETING

    # Check for high-intent signals first (higher priority)
    if _matches_any(msg, HIGH_INTENT_KEYWORDS):
        return INTENT_HIGH_INTENT_LEAD

    # Check for product/pricing inquiry
    if _matches_any(msg, PRODUCT_KEYWORDS):
        return INTENT_PRODUCT_INQUIRY

    # If only greeting keywords, it's a greeting
    if _matches_any(msg, GREETING_KEYWORDS):
        return INTENT_GREETING

    # Default: treat as product inquiry (agent will handle gracefully)
    return INTENT_PRODUCT_INQUIRY


def intent_label(intent: str) -> str:
    labels = {
        INTENT_GREETING: "💬 Greeting",
        INTENT_PRODUCT_INQUIRY: "🔍 Product/Pricing Inquiry",
        INTENT_HIGH_INTENT_LEAD: "🎯 High-Intent Lead"
    }
    return labels.get(intent, "❓ Unknown")
