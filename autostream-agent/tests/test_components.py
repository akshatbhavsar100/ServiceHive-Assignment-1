"""
tests/test_components.py
Unit tests for RAG, intent detection, and lead capture tool.
Run: python -m pytest tests/ -v
  OR: python tests/test_components.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.rag import retrieve, load_knowledge_base, flatten_knowledge
from agent.intent import classify_intent, INTENT_GREETING, INTENT_PRODUCT_INQUIRY, INTENT_HIGH_INTENT_LEAD
from tools.lead_capture import mock_lead_capture, validate_email, validate_platform


# ─────────────────────────────────────────────
# RAG TESTS
# ─────────────────────────────────────────────

def test_knowledge_base_loads():
    kb = load_knowledge_base()
    assert "company" in kb
    assert "plans" in kb
    assert len(kb["plans"]) == 2
    print("✅ Knowledge base loads correctly")


def test_flatten_knowledge():
    kb = load_knowledge_base()
    chunks = flatten_knowledge(kb)
    assert len(chunks) >= 5
    print(f"✅ Knowledge base flattened into {len(chunks)} chunks")


def test_rag_pricing_query():
    result = retrieve("What is the price of the Pro plan?")
    assert "79" in result or "Pro" in result
    print("✅ RAG retrieves Pro plan pricing")


def test_rag_refund_query():
    result = retrieve("What is the refund policy?")
    assert "7 days" in result or "refund" in result.lower()
    print("✅ RAG retrieves refund policy")


def test_rag_support_query():
    result = retrieve("Is 24/7 support available?")
    assert "Pro" in result or "24/7" in result
    print("✅ RAG retrieves support policy")


# ─────────────────────────────────────────────
# INTENT TESTS
# ─────────────────────────────────────────────

def test_intent_greeting():
    assert classify_intent("Hi there!") == INTENT_GREETING
    assert classify_intent("Hello") == INTENT_GREETING
    assert classify_intent("Hey, how are you?") == INTENT_GREETING
    print("✅ Greeting intent detected correctly")


def test_intent_product_inquiry():
    assert classify_intent("What is the price of your Pro plan?") == INTENT_PRODUCT_INQUIRY
    assert classify_intent("Tell me about your features") == INTENT_PRODUCT_INQUIRY
    assert classify_intent("Do you offer refunds?") == INTENT_PRODUCT_INQUIRY
    print("✅ Product inquiry intent detected correctly")


def test_intent_high_intent():
    assert classify_intent("I want to try the Pro plan") == INTENT_HIGH_INTENT_LEAD
    assert classify_intent("That sounds good, sign me up!") == INTENT_HIGH_INTENT_LEAD
    assert classify_intent("I'm ready to subscribe") == INTENT_HIGH_INTENT_LEAD
    assert classify_intent("How do I sign up?") == INTENT_HIGH_INTENT_LEAD
    print("✅ High-intent lead detected correctly")


# ─────────────────────────────────────────────
# LEAD CAPTURE TESTS
# ─────────────────────────────────────────────

def test_mock_lead_capture():
    result = mock_lead_capture("John Doe", "john@example.com", "YouTube")
    assert result["success"] is True
    assert result["name"] == "John Doe"
    assert result["email"] == "john@example.com"
    assert result["platform"] == "YouTube"
    assert "lead_id" in result
    print("✅ Mock lead capture works correctly")


def test_email_validation():
    assert validate_email("john@example.com") is True
    assert validate_email("invalid-email") is False
    assert validate_email("no_at_sign.com") is False
    print("✅ Email validation works correctly")


def test_platform_validation():
    assert validate_platform("YouTube") is True
    assert validate_platform("Instagram") is True
    assert validate_platform("TikTok") is True
    assert validate_platform("MyBlog") is False
    print("✅ Platform validation works correctly")


# ─────────────────────────────────────────────
# RUN ALL TESTS
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  AutoStream Agent — Component Tests")
    print("=" * 50 + "\n")

    tests = [
        test_knowledge_base_loads,
        test_flatten_knowledge,
        test_rag_pricing_query,
        test_rag_refund_query,
        test_rag_support_query,
        test_intent_greeting,
        test_intent_product_inquiry,
        test_intent_high_intent,
        test_mock_lead_capture,
        test_email_validation,
        test_platform_validation,
    ]

    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__} FAILED: {e}")
            failed += 1

    print(f"\n{'=' * 50}")
    print(f"  Results: {passed} passed, {failed} failed")
    print("=" * 50 + "\n")

    if failed > 0:
        sys.exit(1)
