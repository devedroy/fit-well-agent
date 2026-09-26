## Frontend UI
*   Vanilla HTML, CSS, and JavaScript for a lightweight, single-page dashboard and interactive chat interface.

## Backend & Data Layer
*   **Framework:** Flask (Python) to expose REST endpoints and manage state routing.
*   **Storage:** `data/memory.json` for local, zero-dependency persistence of user profiles, conversation history, workout logs, meal logs, and progress tracking. Managed through `database/db_manager.py` with atomic writes.

## Agent Orchestration
*   **Logic Framework:** LangGraph to manage the ReAct cognitive architecture, utilizing a `TypedDict` for the `AgentState` and `add_messages` for conversation history.
*   **LLM Engine:** Google Gemini API (`langchain-google-genai`) configured with `bind_tools()` to enable deterministic function calling.
*   **External APIs:** Google Maps Places API for location-based facility queries.
