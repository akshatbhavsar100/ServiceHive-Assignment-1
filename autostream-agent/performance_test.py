import time
from agent.rag import retrieve

# Test performance with multiple queries
queries = [
    "Hi, tell me about your pricing.",
    "What features does the Pro plan have?",
    "Is there a free trial?",
    "What's your refund policy?",
    "Can I upgrade from Basic to Pro?"
]

print("Performance Test - RAG Retrieval")
print("=" * 40)

total_time = 0
for i, query in enumerate(queries, 1):
    start_time = time.time()
    result = retrieve(query)
    end_time = time.time()
    
    query_time = end_time - start_time
    total_time += query_time
    
    print(f"Query {i}: {query[:30]}...")
    print(f"Time: {query_time:.3f}s")
    print(f"Result length: {len(result)} chars")
    print()

print(f"Total time for {len(queries)} queries: {total_time:.3f}s")
print(f"Average time per query: {total_time/len(queries):.3f}s")
