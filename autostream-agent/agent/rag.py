"""
agent/rag.py
RAG (Retrieval-Augmented Generation) pipeline for AutoStream knowledge base.
Uses simple keyword/semantic search over a local JSON knowledge base.
No vector DB required — keeps the project lightweight and self-contained.
"""

import json
import os
from typing import Optional

# Cache the knowledge base to avoid repeated file loading
_cached_kb = None
_cached_chunks = None


def load_knowledge_base(path: Optional[str] = None) -> dict:
    """Load the JSON knowledge base from disk (cached for performance)."""
    global _cached_kb
    
    if _cached_kb is not None:
        return _cached_kb
        
    if path is None:
        # Get the directory where the current script is located (agent/)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one level to the project root and then to data
        path = os.path.join(script_dir, "..", "data", "knowledge_base.json")
        # Normalize the path to handle .. correctly
        path = os.path.normpath(path)
    with open(path, "r") as f:
        _cached_kb = json.load(f)
    return _cached_kb


def flatten_knowledge(kb: dict) -> list[dict]:
    """
    Flatten the knowledge base into a list of searchable chunks (cached for performance).
    Each chunk has a 'topic' and 'content' field.
    """
    global _cached_chunks
    
    if _cached_chunks is not None:
        return _cached_chunks
        
    chunks = []

    # Company overview
    chunks.append({
        "topic": "company overview",
        "content": f"{kb['company']['name']}: {kb['company']['description']}"
    })

    # Plans
    for plan in kb["plans"]:
        features = "\n  - ".join(plan["features"])
        chunks.append({
            "topic": f"{plan['name'].lower()} pricing plan",
            "content": (
                f"{plan['name']} — {plan['price']}\n"
                f"Features:\n  - {features}"
            )
        })

    # All plans summary
    plans_summary = ""
    for plan in kb["plans"]:
        plans_summary += f"\n{plan['name']} ({plan['price']}): " + ", ".join(plan["features"])
    chunks.append({
        "topic": "all plans pricing comparison",
        "content": "AutoStream offers two plans:" + plans_summary
    })

    # Policies
    for policy in kb["policies"]:
        chunks.append({
            "topic": policy["topic"].lower(),
            "content": f"{policy['topic']}: {policy['details']}"
        })

    # FAQs
    for faq in kb["faqs"]:
        chunks.append({
            "topic": faq["question"].lower(),
            "content": f"Q: {faq['question']}\nA: {faq['answer']}"
        })

    _cached_chunks = chunks
    return chunks


def retrieve(query: str, top_k: int = 3) -> str:
    """
    Retrieve the most relevant knowledge chunks for a given query.
    Uses simple keyword overlap scoring (no embeddings needed).

    Returns a formatted string of retrieved context.
    """
    kb = load_knowledge_base()
    chunks = flatten_knowledge(kb)

    # Clean query terms - remove punctuation and convert to lowercase
    import re
    query_terms = set(re.sub(r'[^\w\s]', '', query.lower()).split())

    scored = []
    for chunk in chunks:
        # Clean chunk terms - remove punctuation and convert to lowercase
        topic_terms = set(re.sub(r'[^\w\s]', '', chunk["topic"].lower()).split())
        content_terms = set(re.sub(r'[^\w\s]', '', chunk["content"].lower()).split())
        all_terms = topic_terms | content_terms

        # Score = keyword overlap
        score = len(query_terms & all_terms)

        # Boost for topic match
        topic_overlap = len(query_terms & topic_terms)
        score += topic_overlap * 2

        scored.append((score, chunk["content"]))

    # Sort by score descending
    scored.sort(key=lambda x: x[0], reverse=True)

    # Return top-k relevant chunks
    top_chunks = [content for score, content in scored[:top_k] if score > 0]

    if not top_chunks:
        return "No specific information found in the knowledge base."

    return "\n\n---\n\n".join(top_chunks)


if __name__ == "__main__":
    # Quick test
    test_queries = [
        "What is the price of the Pro plan?",
        "Do you offer refunds?",
        "Is 4K resolution available?",
        "What is AutoStream?"
    ]
    for q in test_queries:
        print(f"\nQuery: {q}")
        print(f"Result:\n{retrieve(q)}")
        print("-" * 60)
