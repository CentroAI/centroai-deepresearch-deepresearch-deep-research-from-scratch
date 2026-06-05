
"""Full Research Pipeline — scoping + research + report generation."""

from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

from deep_research_from_scratch.utils import get_today_str
from deep_research_from_scratch.prompts import final_report_generation_prompt
from deep_research_from_scratch.state_scope import AgentState, AgentInputState
from deep_research_from_scratch.research_agent_scope import clarify_with_user, write_research_brief
from deep_research_from_scratch.research_agent import researcher_agent


# ══════════════════════════════════════════════════════
# MODEL
# ══════════════════════════════════════════════════════

# Same model as the rest of the course — consistent and free
writer_model = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.0, max_tokens=4000)


# ══════════════════════════════════════════════════════
# BRIDGE NODE — run_research
# Connects Phase 1 (AgentState) to Phase 2 (ResearcherState)
# Reads  : state["research_brief"]
# Writes : state["notes"]  ← compressed research for report generation
# ══════════════════════════════════════════════════════

def run_research(state: AgentState) -> dict:
    """Bridge node: invoke the research agent and store results in AgentState."""
    research_brief = state.get("research_brief", "")

    # Run the research agent from Notebook 2
    # It takes a ResearcherState input, returns ResearcherOutputState
    result = researcher_agent.invoke({
        "researcher_messages": [HumanMessage(content=f"{research_brief}.")]
    })

    # Bridge the results back into AgentState
    return {
        "notes": [result["compressed_research"]],  # store as list — final_report_generation joins it
    }


# ══════════════════════════════════════════════════════
# NODE — final_report_generation
# Reads  : state["notes"], state["research_brief"]
# Writes : state["final_report"], state["messages"]
# ══════════════════════════════════════════════════════

def final_report_generation(state: AgentState) -> dict:
    """Synthesise all research findings into a comprehensive final report."""

    # Join all note chunks into one findings string
    findings = "\n\n".join(state.get("notes", []))

    # Format the prompt with real data from state
    prompt = final_report_generation_prompt.format(
        research_brief=state.get("research_brief", ""),
        findings=findings,
        date=get_today_str(),
    )

    # Call the model — free-form markdown, no structured output schema
    response = writer_model.invoke([HumanMessage(content=prompt)])

    return {
        "final_report": response.content,
        "messages":     [HumanMessage(content="Here is your final report:\n\n" + response.content)],
    }


# ══════════════════════════════════════════════════════
# GRAPH CONSTRUCTION
# Full pipeline: scope → research → report
# ══════════════════════════════════════════════════════

deep_researcher_builder = StateGraph(AgentState, input_schema=AgentInputState)

# ── Nodes ────────────────────────────────────────────
deep_researcher_builder.add_node("clarify_with_user",       clarify_with_user)      # NB1
deep_researcher_builder.add_node("write_research_brief",    write_research_brief)   # NB1
deep_researcher_builder.add_node("run_research",            run_research)           # bridge
deep_researcher_builder.add_node("final_report_generation", final_report_generation) # new

# ── Edges ────────────────────────────────────────────
deep_researcher_builder.add_edge(START,                    "clarify_with_user")
# clarify_with_user uses Command internally → routes to write_research_brief or END
deep_researcher_builder.add_edge("write_research_brief",   "run_research")
deep_researcher_builder.add_edge("run_research",           "final_report_generation")
deep_researcher_builder.add_edge("final_report_generation", END)
