## Phase 1: Foundation & Data Layer
1.  Scaffold the Flask application structure and core API routes.
2.  Initialize the SQLite database using `schema.sql` and populate it with initial dummy data for testing.
3.  Establish environment variables for the Gemini and Google Maps API keys.

## Phase 2: Core Agent Logic (LangGraph + Gemini)
1.  Define the Python functions for database operations and Maps queries, decorating them with LangChain's `@tool`.
2.  Establish the `AgentState` dictionary to track conversation history and tool execution outputs.
3.  Compile the LangGraph by defining the reasoning node (Gemini) and the tool-execution node, linking them with conditional edges.

## Phase 3: Integration & Delivery
1.  Connect the Flask `/api/chat` route to invoke the compiled LangGraph object.
2.  Wire the frontend dashboard to fetch and visualize SQLite data dynamically.
3.  Finalize the chat interface to process user inputs and stream the agent's responses.
