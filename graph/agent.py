"""
FitWell LangGraph Agent.

Graph topology:
  START → reason → [tool_node | END]
            ↑______________|

The 'reason' node calls the configured LLM (Ollama or Gemini) with tool bindings.
If the LLM requests a tool call, the graph routes to 'tool_node',
executes the tools, and feeds the results back into 'reason'.
Otherwise the graph terminates and returns the final AI message.
"""

import os
from dotenv import load_dotenv

load_dotenv()

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition

from graph.state import AgentState
from graph.tools import ALL_TOOLS
from database.db_manager import get_user_profile, append_message


def _get_llm():
    """Retrieve LLM client configured for either local Ollama or Google Gemini."""
    load_dotenv(override=True)
    provider = os.getenv("LLM_PROVIDER", "ollama").strip().lower()

    if provider == "ollama":
        from langchain_ollama import ChatOllama
        model_name = os.getenv("OLLAMA_MODEL", "gemma4:e4b").strip()
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").strip()
        return ChatOllama(
            model=model_name,
            base_url=base_url,
            temperature=0.7,
        ).bind_tools(ALL_TOOLS)

    # Fallback to Google Gemini
    from langchain_google_genai import ChatGoogleGenerativeAI
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or api_key == "your_gemini_api_key_here":
        raise ValueError(
            "Gemini API key is not configured. Please set a valid GEMINI_API_KEY in your .env file, "
            "or set LLM_PROVIDER=ollama to run locally."
        )
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    return ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=api_key,
        temperature=0.7,
    ).bind_tools(ALL_TOOLS)


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
    """LLM reasoning node: calls LLM with the full message history and bound tools."""
    llm_with_tools = _get_llm()
    messages = [SystemMessage(content=_SYSTEM_PROMPT)] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


# ── Graph Assembly ────────────────────────────────────────────────────────────

def build_graph():
    builder = StateGraph(AgentState)

    builder.add_node("reason", reason)
    builder.add_node("tools", ToolNode(ALL_TOOLS))

    builder.add_edge(START, "reason")
    builder.add_conditional_edges("reason", tools_condition)
    builder.add_edge("tools", "reason")

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

    load_dotenv(override=True)
    provider = os.getenv("LLM_PROVIDER", "ollama").strip().lower()
    api_key = os.getenv("GEMINI_API_KEY", "").strip()

    # Guard check only when Gemini is explicitly chosen as provider
    if provider == "gemini" and (not api_key or api_key == "your_gemini_api_key_here"):
        append_message("user", user_message)
        reply = (
            "👋 Hello! I'm FitWell, your AI fitness and wellness coach.\n\n"
            "⚠️ **Gemini API Key Required**: Please update `GEMINI_API_KEY` in your `.env` file with a valid Google Gemini API key to activate intelligent agent reasoning.\n\n"
            "💡 *Tip: You can set `LLM_PROVIDER=ollama` in `.env` to run completely offline and free using local models like `gemma4:e4b`!*\n\n"
            "In the meantime, your local database is initialized! You can explore the **Dashboard**, log workouts and meals, track body metrics, and browse nearby gyms in the **Facilities** tab."
        )
        append_message("assistant", reply)
        return reply

    # Persist the incoming user message
    append_message("user", user_message)

    # Reconstruct history for the LLM context (up to recent 20 turns)
    history = get_conversation_history()
    lc_messages = []
    for turn in history[-20:]:
        role = turn.get("role")
        content = turn.get("content", "")
        if role == "user":
            lc_messages.append(HumanMessage(content=content))
        elif role == "assistant":
            lc_messages.append(AIMessage(content=content))

    initial_state: AgentState = {
        "messages": lc_messages,
        "user_profile": get_user_profile(),
    }

    try:
        final_state = graph.invoke(initial_state)
        ai_message = final_state["messages"][-1]
        raw_content = getattr(ai_message, "content", str(ai_message))
        if isinstance(raw_content, list):
            parts = []
            for item in raw_content:
                if isinstance(item, dict) and "text" in item:
                    parts.append(item["text"])
                elif isinstance(item, str):
                    parts.append(item)
                else:
                    parts.append(str(item))
            response_text = "".join(parts)
        else:
            response_text = str(raw_content)
    except Exception as exc:
        if provider == "ollama":
            ollama_model = os.getenv("OLLAMA_MODEL", "gemma4:e4b")
            response_text = (
                f"⚠️ An error occurred while communicating with Ollama (`{ollama_model}`): {str(exc)}\n\n"
                "Please verify that Ollama is running (`ollama serve` or desktop app) and that the model is loaded."
            )
        else:
            response_text = (
                f"⚠️ An error occurred while communicating with the Gemini model: {str(exc)}\n\n"
                "Please check that your GEMINI_API_KEY is valid and has sufficient quota."
            )

    # Persist the assistant reply
    append_message("assistant", response_text)
    return response_text
