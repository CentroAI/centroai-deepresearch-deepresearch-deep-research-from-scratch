
"""State Definitions and Pydantic Schemas for Research Scoping."""

from typing_extensions import Optional, Annotated, Sequence

from langgraph.graph import MessagesState
from pydantic import BaseModel, Field


# ══════════════════════════════════════════════════════
# STATE DEFINITIONS — the whiteboard
# ══════════════════════════════════════════════════════

class AgentInputState(MessagesState):
    """What the USER provides: only the conversation messages."""
    pass


class AgentState(MessagesState):
    """The full internal whiteboard — read and written by every node."""

    # ── Phase 1: Scoping ─────────────────────────────────────────
    # Written by write_research_brief, read by the research phase
    research_brief: Optional[str]

    # ── Phase 2: Research ────────────────────────────────────────
    # Compressed research summary passed to the report node
    notes: list[str]

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
