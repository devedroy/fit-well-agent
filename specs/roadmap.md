## Phase 1: Foundation & Data Layer
1.  Scaffold the Flask application structure and core API routes.
2.  Create `data/memory.json` with the full schema (user profile, conversation history, workout history, meal logs, progress tracking) and populate it with realistic starter data using `database/seed_data.py`.
3.  Establish environment variables for the Gemini and Google Maps API keys in `.env`.

## Phase 2: Core Agent Logic (LangGraph + Gemini)
1.  Define Python functions in `database/db_manager.py` for all memory read/write operations (profile, messages, workouts, meals, progress).
2.  Decorate agent-facing wrappers in `graph/tools.py` with LangChain's `@tool` so Gemini can invoke them via function-calling.
3.  Establish the `AgentState` TypedDict (`graph/state.py`) to track conversation history and user profile across graph nodes.
4.  Compile the LangGraph by defining the reasoning node (Gemini) and the tool-execution node (`ToolNode`), linking them with conditional edges via `tools_condition`.

## Phase 3: Integration & Delivery
1.  Connect the Flask `/api/chat` route to invoke the compiled LangGraph object via `graph/agent.py:chat()`.
2.  Wire the frontend dashboard (`static/js/dashboard.js`) to fetch and visualize `memory.json` data dynamically through the REST API.
3.  Finalize the chat interface (`static/js/chat.js`) to process user inputs and render the agent's responses.
