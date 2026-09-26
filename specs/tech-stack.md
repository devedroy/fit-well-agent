## Frontend UI
*   Vanilla HTML, CSS, and JavaScript for a lightweight, single-page dashboard and interactive chat interface.

## Backend & Data Layer
*   **Framework:** Flask (Python) to expose REST endpoints and manage state routing.
*   **Database:** SQLite for local, serverless persistence of user profiles and progress logs.

## Agent Orchestration
*   **Logic Framework:** LangGraph to manage the ReAct cognitive architecture, utilizing a `TypedDict` for the `AgentState` and `add_messages` for conversation history.
*   **LLM Engine:** Google Gemini API (`langchain-google-genai`) configured with `bind_tools()` to enable deterministic function calling.
*   **External APIs:** Google Maps Places API for location-based facility queries.
