
"""State Definitions and Pydantic Schemas for Research Scoping."""

import operator
from typing_extensions import Optional, Annotated, Sequence

from langchain_core.messages import BaseMessage
from langgraph.graph import MessagesState
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field


# ══════════════════════════════════════════════════════
# STATE DEFINITIONS — the whiteboard
# ══════════════════════════════════════════════════════

class AgentInputState(MessagesState):
    """What the USER provides: only the conversation messages."""
    pass


class AgentState(MessagesState):
    """The full internal whiteboard — read and written by every node.

    Fields marked with operator.add are MERGED (not overwritten) when
    multiple parallel agents write to them at the same time.
    """

    # ── Phase 1: Scoping ─────────────────────────────────────────
    # Written by write_research_brief, read by Phase 2 agents
    research_brief: Optional[str]

    # ── Phase 2: Research coordination ──────────────────────────
    # Uses add_messages → new messages are appended, never replaced
    supervisor_messages: Annotated[Sequence[BaseMessage], add_messages]

    # Uses operator.add → lists from parallel agents are concatenated
    raw_notes: Annotated[list[str], operator.add] = []
    notes:     Annotated[list[str], operator.add] = []

    # ── Phase 3: Output ──────────────────────────────────────────
    final_report: str


# ══════════════════════════════════════════════════════
# STRUCTURED OUTPUT SCHEMAS — the forms
# ══════════════════════════════════════════════════════

class ClarifyWithUser(BaseModel):
    """Form filled by the LLM in Node 1 — routing decision + message."""

    need_clarification: bool = Field(
        description="True if the user request is too vague to research. False if we have enough to proceed.",
    )
    question: str = Field(
        description="The clarifying question to show the user if need_clarification is True.",
    )
    verification: str = Field(
        description="A friendly confirmation shown to the user when need_clarification is False.",
    )


class ResearchQuestion(BaseModel):
    """Form filled by the LLM in Node 2 — the research brief."""

    research_brief: str = Field(
        description="A detailed research specification distilled from the full conversation history.",
    )
