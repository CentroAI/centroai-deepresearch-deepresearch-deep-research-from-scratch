
"""Workflow nodes for the scoping phase — clarification and brief generation."""

from datetime import datetime
from typing_extensions import Literal

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, get_buffer_string
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command

from deep_research_from_scratch.prompts import (
    clarify_with_user_instructions,
    transform_messages_into_research_topic_prompt,
)
from deep_research_from_scratch.state_scope import (
    AgentState, AgentInputState,
    ClarifyWithUser, ResearchQuestion,
)


# ── Utility ──────────────────────────────────────────────────
def get_today_str() -> str:
    """Return today's date as a readable string (Windows-safe)."""
    return datetime.now().strftime("%a %b %d, %Y").replace(" 0", " ")


# ── Model ────────────────────────────────────────────────────
model = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.0)


# ══════════════════════════════════════════════════════
# NODE 1 — clarify_with_user
# Purpose : decide if we need more info from the user
# Reads   : state["messages"]
# Writes  : a new AIMessage (question OR confirmation)
# Routes  : END (ask user) or write_research_brief (proceed)
# ══════════════════════════════════════════════════════

def clarify_with_user(state: AgentState) -> Command[Literal["write_research_brief", "__end__"]]:

    # Step 1 — attach the schema (the "form") to the model
    structured_model = model.with_structured_output(ClarifyWithUser)

    # Step 2 — invoke with the prompt filled from state
    response = structured_model.invoke([
        HumanMessage(content=clarify_with_user_instructions.format(
            messages=get_buffer_string(messages=state["messages"]),
            date=get_today_str()
        ))
    ])
    # response is now a ClarifyWithUser object — not raw text

    # Step 3 — route based on the bool field
    if response.need_clarification:
        # Not enough info → stop and show the question to the user
        return Command(
            goto=END,
            update={"messages": [AIMessage(content=response.question)]}
        )
    else:
        # Enough info → continue to write the brief
        return Command(
            goto="write_research_brief",
            update={"messages": [AIMessage(content=response.verification)]}
        )


# ══════════════════════════════════════════════════════
# NODE 2 — write_research_brief
# Purpose : distil the conversation into a research brief
# Reads   : state["messages"]  (the full conversation)
# Writes  : research_brief, supervisor_messages
# Routes  : always → END  (no decision needed, plain dict return)
# ══════════════════════════════════════════════════════

def write_research_brief(state: AgentState):

    # Step 1 — attach the schema
    structured_model = model.with_structured_output(ResearchQuestion)

    # Step 2 — invoke with the full conversation history
    response = structured_model.invoke([
        HumanMessage(content=transform_messages_into_research_topic_prompt.format(
            messages=get_buffer_string(state.get("messages", [])),
            date=get_today_str()
        ))
    ])

    # Step 3 — write to state (plain dict, no routing decision needed)
    return {
        "research_brief": response.research_brief,
        # Also forward the brief to Phase 2 via supervisor_messages
        "supervisor_messages": [HumanMessage(content=f"{response.research_brief}.")]
    }


# ══════════════════════════════════════════════════════
# GRAPH CONSTRUCTION — wire the nodes together
# ══════════════════════════════════════════════════════

deep_researcher_builder = StateGraph(AgentState, input_schema=AgentInputState)

deep_researcher_builder.add_node("clarify_with_user",    clarify_with_user)
deep_researcher_builder.add_node("write_research_brief", write_research_brief)

deep_researcher_builder.add_edge(START, "clarify_with_user")
deep_researcher_builder.add_edge("write_research_brief", END)

# Compile without checkpointer (used when importing into later notebooks)
scope_research = deep_researcher_builder.compile()
