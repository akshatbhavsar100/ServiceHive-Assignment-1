from agent.graph import llm
from langchain_core.messages import HumanMessage, SystemMessage

# Test the LLM directly
system_prompt = """You are Alex, a friendly sales assistant for AutoStream.
Answer the following question using only this information:

Basic Plan: $29/month - 10 videos, 720p, basic editing
Pro Plan: $79/month - unlimited videos, 4K, AI captions, advanced editing
"""

messages = [
    SystemMessage(content=system_prompt),
    HumanMessage(content="Hi, tell me about your pricing.")
]

print("Testing LLM directly...")
print("Model:", llm.model)
print()

try:
    response = llm.invoke(messages)
    print("Response type:", type(response))
    print("Response content type:", type(response.content))
    print("Raw response:", response)
    print()
    print("Extracted content:", response.content)
except Exception as e:
    print("Error:", e)
