
"""State Definitions and Pydantic Schemas for the Research Agent."""

import operator
from typing_extensions import TypedDict, Annotated, List, Sequence
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


# ══════════════════════════════════════════════════════
# STATE DEFINITIONS
# ══════════════════════════════════════════════════════

class ResearcherState(TypedDict):
    """Internal whiteboard — everything the agent tracks while working."""
    researcher_messages: Annotated[Sequence[BaseMessage], add_messages]
    tool_call_iterations: int        # how many tool rounds completed
    research_topic: str              # the research brief from Phase 1
    compressed_research: str         # final compressed summary
    raw_notes: Annotated[List[str], operator.add]  # merged safely across parallel agents


class ResearcherOutputState(TypedDict):
    """Clean handoff package — only results, no internal bookkeeping."""
    compressed_research: str
    raw_notes: Annotated[List[str], operator.add]
    researcher_messages: Annotated[Sequence[BaseMessage], add_messages]


# ══════════════════════════════════════════════════════
# STRUCTURED OUTPUT SCHEMAS
# ══════════════════════════════════════════════════════

class Summary(BaseModel):
    """Form the LLM fills to summarise a raw webpage into clean, useful content."""
    summary: str = Field(description="Concise summary of the webpage content")
    key_excerpts: str = Field(description="Important quotes and excerpts from the content")
