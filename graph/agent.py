"""
FitWell LangGraph Agent.

Graph topology:
  START → reason → [tool_node | END]
            ↑______________|

The 'reason' node calls Gemini with tool bindings.
If Gemini requests a tool call, the graph routes to 'tool_node',
executes the tools, and feeds the results back into 'reason'.
Otherwise the graph terminates and returns the final AI message.
"""

import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition

from graph.state import AgentState
from graph.tools import ALL_TOOLS
from database.db_manager import get_user_profile, append_message

# ── LLM ──────────────────────────────────────────────────────────────────────
_llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=os.environ["GEMINI_API_KEY"],
    temperature=0.7,
)
_llm_with_tools = _llm.bind_tools(ALL_TOOLS)

# ── System Prompt ─────────────────────────────────────────────────────────────
_SYSTEM_PROMPT = """You are FitWell, a personalized fitness and wellness AI assistant.

Your role:
- Provide tailored workout plans, meal plans, and health advice.
- Always fetch the user's profile first (use fetch_user_profile) to personalise your response.
- Log user inputs to memory when they share new data (weight, workouts, meals).
- Be encouraging, specific, and data-driven.
- When the user provides personal details (age, weight, goal, etc.), save them immediately using save_user_profile.

Tone: Friendly, motivating, and concise. Avoid generic advice."""


# ── Nodes ─────────────────────────────────────────────────────────────────────

def reason(state: AgentState) -> dict:
    """LLM reasoning node: calls Gemini with the full message history."""
    messages = [SystemMessage(content=_SYSTEM_PROMPT)] + state["messages"]
    response = _llm_with_tools.invoke(messages)
    return {"messages": [response]}


# ── Graph Assembly ────────────────────────────────────────────────────────────

def build_graph():
    builder = StateGraph(AgentState)

    builder.add_node("reason", reason)
    builder.add_node("tool_node", ToolNode(ALL_TOOLS))

    builder.add_edge(START, "reason")
    builder.add_conditional_edges("reason", tools_condition)
    builder.add_edge("tool_node", "reason")

    return builder.compile()


# Compiled graph — imported by Flask routes
graph = build_graph()


# ── Graph Visualisation ───────────────────────────────────────────────────────

def display_graph():
    """
    Render the compiled LangGraph topology inline.

    In a Jupyter / IPython environment this renders as a PNG image cell.
    In a plain Python script it saves 'agent_graph.png' to the project root
    and prints the path.

    Usage:
        from graph.agent import display_graph
        display_graph()
    """
    try:
        from IPython.display import display, Image  # type: ignore
        png_bytes = graph.get_graph().draw_mermaid_png()
        display(Image(png_bytes))
    except ImportError:
        # Fallback: save to disk when IPython is not available
        import pathlib
        out = pathlib.Path(__file__).parent.parent / "agent_graph.png"
        png_bytes = graph.get_graph().draw_mermaid_png()
        out.write_bytes(png_bytes)
        print(f"Graph saved → {out}")


# ── Public API ────────────────────────────────────────────────────────────────

def chat(user_message: str) -> str:
    """
    Run one conversational turn through the graph.

    Args:
        user_message: Raw text from the user.

    Returns:
        The agent's final text response.
    """
    from database.db_manager import get_conversation_history

    # Persist the incoming user message
    append_message("user", user_message)

    # Reconstruct full history for the LLM context
    history = get_conversation_history()
    lc_messages = []
    for turn in history:
        if turn["role"] == "user":
            lc_messages.append(HumanMessage(content=turn["content"]))
        # assistant messages will be re-generated; we only feed user turns
        # to keep the state clean (the LLM reconstructs its own turns from context)

    initial_state: AgentState = {
        "messages": lc_messages,
        "user_profile": get_user_profile(),
    }

    final_state = graph.invoke(initial_state)

    # Extract the last AI message
    ai_message = final_state["messages"][-1]
    response_text = ai_message.content

    # Persist the assistant reply
    append_message("assistant", response_text)

    return response_text
