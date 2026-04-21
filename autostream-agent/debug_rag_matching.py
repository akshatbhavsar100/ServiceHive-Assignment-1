from agent.rag import load_knowledge_base, flatten_knowledge
import json

# Load and flatten knowledge base
kb = load_knowledge_base()
chunks = flatten_knowledge(kb)

query = "Hi, tell me about your pricing."
query_terms = set(query.lower().split())

print("Query:", query)
print("Query terms:", query_terms)
print()

# Check each chunk for matching
for i, chunk in enumerate(chunks):
    topic_terms = set(chunk["topic"].lower().split())
    content_terms = set(chunk["content"].lower().split())
    all_terms = topic_terms | content_terms
    
    # Score = keyword overlap
    score = len(query_terms & all_terms)
    
    # Boost for topic match
    topic_overlap = len(query_terms & topic_terms)
    score += topic_overlap * 2
    
    print(f"Chunk {i+1} ({chunk['topic']}):")
    print(f"  Score: {score}")
    print(f"  Topic overlap: {topic_overlap}")
    print(f"  Content overlap: {len(query_terms & content_terms)}")
    print(f"  Matching terms: {query_terms & all_terms}")
    print(f"  Content preview: {chunk['content'][:100]}...")
    print()
