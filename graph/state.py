"""
AgentState: The TypedDict that flows through every node of the LangGraph.
All inter-node communication travels through this object.
"""

from typing import Annotated, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    # add_messages reducer: appends new messages instead of overwriting
    messages: Annotated[list[BaseMessage], add_messages]
    # Snapshot of the user profile, refreshed at the start of each turn
    user_profile: dict
