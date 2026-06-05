
"""Research Agent — iterative web search and synthesis."""

from typing_extensions import Literal

from langgraph.graph import StateGraph, START, END
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from langchain_groq import ChatGroq

from deep_research_from_scratch.state_research import ResearcherState, ResearcherOutputState
from deep_research_from_scratch.utils import tavily_search, get_today_str, think_tool
from deep_research_from_scratch.prompts import (
    research_agent_prompt,
    compress_research_system_prompt,
    compress_research_human_message,
)


# ══════════════════════════════════════════════════════
# CONFIGURATION
# ══════════════════════════════════════════════════════

tools = [tavily_search, think_tool]
tools_by_name = {tool.name: tool for tool in tools}

# Main agent model — handles tool calling decisions
model = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.0)
model_with_tools = model.bind_tools(tools)

# Compression model — higher token limit to avoid cutting off mid-sentence
compress_model = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.0, max_tokens=4000)


# ══════════════════════════════════════════════════════
# NODE 1 — llm_call
# The brain: reads all messages, decides what to do next
# ══════════════════════════════════════════════════════

def llm_call(state: ResearcherState):
    """Let the LLM decide: call a tool (search/think) or finish."""
    return {
        "researcher_messages": [
            model_with_tools.invoke(
                [SystemMessage(content=research_agent_prompt)] + state["researcher_messages"]
            )
        ]
    }


# ══════════════════════════════════════════════════════
# NODE 2 — tool_node
# The hands: executes every tool call from the last AI message
# ══════════════════════════════════════════════════════

def tool_node(state: ResearcherState):
    """Execute every tool call from the last LLM response."""
    tool_calls = state["researcher_messages"][-1].tool_calls

    observations = []
    for tool_call in tool_calls:
        tool_fn = tools_by_name[tool_call["name"]]
        observations.append(tool_fn.invoke(tool_call["args"]))

    tool_outputs = [
        ToolMessage(
            content=observation,
            name=tool_call["name"],
            tool_call_id=tool_call["id"],
        )
        for observation, tool_call in zip(observations, tool_calls)
    ]

    return {"researcher_messages": tool_outputs}


# ══════════════════════════════════════════════════════
# NODE 3 — compress_research
# The writer: reads all messages, writes the final summary
# ══════════════════════════════════════════════════════

def compress_research(state: ResearcherState) -> dict:
    """Compress the full research trajectory into a concise summary."""
    system_message = compress_research_system_prompt.format(date=get_today_str())

    messages = (
        [SystemMessage(content=system_message)]
        + state.get("researcher_messages", [])
        + [HumanMessage(content=compress_research_human_message)]  # re-anchors the topic
    )
    response = compress_model.invoke(messages)

    return {
        "compressed_research": str(response.content),
    }


# ══════════════════════════════════════════════════════
# ROUTING — should_continue
# Not a node — a function used by add_conditional_edges
# ══════════════════════════════════════════════════════

def should_continue(state: ResearcherState) -> Literal["tool_node", "compress_research"]:
    """Route based on whether the last AI message has tool calls."""
    last_message = state["researcher_messages"][-1]
    if last_message.tool_calls:
        return "tool_node"
    return "compress_research"


# ══════════════════════════════════════════════════════
# GRAPH CONSTRUCTION
# ══════════════════════════════════════════════════════

agent_builder = StateGraph(ResearcherState, output_schema=ResearcherOutputState)

agent_builder.add_node("llm_call",          llm_call)
agent_builder.add_node("tool_node",         tool_node)
agent_builder.add_node("compress_research", compress_research)

agent_builder.add_edge(START, "llm_call")

agent_builder.add_conditional_edges(
    "llm_call",
    should_continue,
    {
        "tool_node":         "tool_node",
        "compress_research": "compress_research",
    },
)

agent_builder.add_edge("tool_node",         "llm_call")   # ← THE LOOP
agent_builder.add_edge("compress_research", END)

# Compile — no checkpointer needed (research agent is stateless between runs)
researcher_agent = agent_builder.compile()
