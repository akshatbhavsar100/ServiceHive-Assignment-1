import os
from agent.rag import load_knowledge_base, flatten_knowledge

print("Current working directory:", os.getcwd())
kb_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "knowledge_base.json")
print("Knowledge base path:", kb_path)

kb = load_knowledge_base()
print("\n=== KNOWLEDGE BASE CONTENT ===")
print(f"Company: {kb['company']['name']}")
print("\n=== PLANS ===")
for plan in kb["plans"]:
    print(f"{plan['name']}: {plan['price']}")
    for feature in plan["features"]:
        print(f"  - {feature}")
print("\n=== FLATTENED CHUNKS ===")
chunks = flatten_knowledge(kb)
for i, chunk in enumerate(chunks[:5]):  # Show first 5 chunks
    print(f"\nChunk {i+1} ({chunk['topic']}):")
    print(chunk['content'][:200] + "...")
