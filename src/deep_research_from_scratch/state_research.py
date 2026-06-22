
"""State Definitions and Pydantic Schemas for the Research Agent."""

from typing_extensions import TypedDict, Annotated, Sequence
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


# ══════════════════════════════════════════════════════
# STATE DEFINITIONS
# ══════════════════════════════════════════════════════

class ResearcherState(TypedDict):
    """The research agent's whiteboard — read and written by every node."""
    researcher_messages: Annotated[Sequence[BaseMessage], add_messages]
    compressed_research: str         # final compressed summary


# ══════════════════════════════════════════════════════
# STRUCTURED OUTPUT SCHEMAS
# ══════════════════════════════════════════════════════

class Summary(BaseModel):
    """Form the LLM fills to summarise a raw webpage into clean, useful content."""
    summary: str = Field(description="Concise summary of the webpage content")
    key_excerpts: str = Field(description="Important quotes and excerpts from the content")
