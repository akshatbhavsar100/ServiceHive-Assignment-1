from agent.rag import retrieve

# Test the exact query that was failing
query = "Hi, tell me about your pricing."
result = retrieve(query)
print("Query:", query)
print("Retrieved context:")
print(result)
print("=" * 50)
print("Length of context:", len(result))
print("Contains pricing info:", "$29" in result or "$79" in result)
