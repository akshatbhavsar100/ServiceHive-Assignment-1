"""
main.py
CLI entrypoint for the AutoStream Social-to-Lead Agent.
Run: python main.py
"""

import sys
from langchain_core.messages import HumanMessage
from agent.graph import autostream_graph, initial_state
from agent.intent import intent_label

BANNER = """
╔══════════════════════════════════════════════════════════╗
║          AutoStream – Social-to-Lead AI Agent            ║
║          Powered by LangGraph + Gemini 1.5 Flash         ║
╚══════════════════════════════════════════════════════════╝
Type your message and press Enter. Type 'quit' or 'exit' to stop.
"""


def run_cli():
    print(BANNER)
    state = initial_state()

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nGoodbye! 👋")
            break

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "bye", "q"):
            print("Agent: Thanks for chatting! Have a great day! 👋")
            break

        # Add user message to state
        state["messages"] = state["messages"] + [HumanMessage(content=user_input)]

        # Run the graph
        try:
            result = autostream_graph.invoke(state)
        except Exception as e:
            print(f"[ERROR] Agent encountered an issue: {e}")
            continue

        # Update state
        state = result

        # Print intent (debug mode)
        intent = state.get("intent", "")
        if intent:
            print(f"  [{intent_label(intent)}]")

        # Print agent response
        last_ai = next(
            (m for m in reversed(state["messages"]) if hasattr(m, "type") and m.type == "ai"),
            None
        )
        if last_ai:
            print(f"Agent: {last_ai.content}\n")

        # Check if lead was just captured
        if state.get("lead_captured") and state.get("stage") == "capturing":
            state["stage"] = "done"


if __name__ == "__main__":
    run_cli()
