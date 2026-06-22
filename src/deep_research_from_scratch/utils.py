
"""Research Utilities and Tools."""

from datetime import datetime
from typing_extensions import Annotated, List

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool, InjectedToolArg
from tavily import TavilyClient

from deep_research_from_scratch.state_research import Summary
from deep_research_from_scratch.prompts import summarize_webpage_prompt


# ══════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ══════════════════════════════════════════════════════

def get_today_str() -> str:
    """Return today's date as a readable string (Windows-safe)."""
    return datetime.now().strftime("%a %b %d, %Y").replace(" 0", " ")


# ══════════════════════════════════════════════════════
# MODEL & CLIENT CONFIGURATION
# ══════════════════════════════════════════════════════

# Used ONLY for webpage summarisation — a light structured output task
summarization_model = ChatGroq(model="llama-3.1-8b-instant", temperature=0.0)

# Tavily reads TAVILY_API_KEY from os.environ automatically
tavily_client = TavilyClient()


# ══════════════════════════════════════════════════════
# SEARCH PIPELINE (internal helpers)
# ══════════════════════════════════════════════════════

def tavily_search_multiple(
    search_queries: List[str],
    max_results: int = 2,
    include_raw_content: bool = True,
) -> List[dict]:
    """Run Tavily searches and return raw results."""
    search_docs = []
    for query in search_queries:
        result = tavily_client.search(
            query,
            max_results=max_results,
            include_raw_content=include_raw_content,
            )
        search_docs.append(result)
    return search_docs


# Groq free tier: ~12k TPM. 6 000 chars ≈ 1 500 tokens — safe margin.
MAX_CONTENT_CHARS = 8_000

def summarize_webpage_content(webpage_content: str) -> str:
    """Truncate then summarise raw webpage content."""
    truncated = webpage_content[:MAX_CONTENT_CHARS]
    if len(webpage_content) > MAX_CONTENT_CHARS:
        truncated += "\n...[content truncated to fit token limit]"
    try:
        structured_model = summarization_model.with_structured_output(Summary, method="json_mode")
        summary = structured_model.invoke([
            HumanMessage(content=summarize_webpage_prompt.format(
                webpage_content=truncated,
                date=get_today_str(),
            ))
        ])
        return (
            f"<summary>\n{summary.summary}\n</summary>\n\n"
            f"<key_excerpts>\n{summary.key_excerpts}\n</key_excerpts>"
        )
    except Exception as e:
        print(f"Failed to summarise webpage: {e}")
        return truncated[:1000] + "..." if len(truncated) > 1000 else truncated


def deduplicate_search_results(search_results: List[dict]) -> dict:
    """Remove duplicate URLs across multiple search responses."""
    unique_results = {}
    for response in search_results:
        for result in response["results"]:
            url = result["url"]
            if url not in unique_results:
                unique_results[url] = result
    return unique_results


def process_search_results(unique_results: dict) -> dict:
    """Summarise each unique result's content."""
    summarized_results = {}
    for url, result in unique_results.items():
        content = (
            summarize_webpage_content(result["raw_content"])
            if result.get("raw_content")
            else result["content"]
        )
        summarized_results[url] = {"title": result["title"], "content": content}
    return summarized_results


def format_search_output(summarized_results: dict) -> str:
    """Format results into a clean readable string for the agent."""
    if not summarized_results:
        return "No valid search results found. Try different queries."
    output = "Search results:\n\n"
    for i, (url, result) in enumerate(summarized_results.items(), 1):
        output += f"\n\n--- SOURCE {i}: {result['title']} ---\n"
        output += f"URL: {url}\n\n"
        output += f"SUMMARY:\n{result['content']}\n\n"
        output += "-" * 80 + "\n"
    return output


# ══════════════════════════════════════════════════════
# LANGCHAIN TOOLS  (what the LLM can call)
# ══════════════════════════════════════════════════════

@tool(parse_docstring=True)
def tavily_search(
    query: str,
    max_results: Annotated[int, InjectedToolArg] = 2,
) -> str:
    """Search the web for information.

    Args:
        query: A single, specific search query
        max_results: Maximum number of results to return

    Returns:
        Formatted string of search results with summaries
    """
    search_results = tavily_search_multiple(
        [query], max_results=max_results, include_raw_content=True,
    )
    unique_results  = deduplicate_search_results(search_results)
    summarized      = process_search_results(unique_results)
    return format_search_output(summarized)


@tool(parse_docstring=True)
def think_tool(reflection: str) -> str:
    """Pause and reflect on research progress before deciding next steps.

    Use this after every search to assess:
    1. What key information did I just find?
    2. What is still missing from my research?
    3. Do I have enough to answer the question comprehensively?
    4. What should my next action be?

    Args:
        reflection: Your detailed reflection on findings, gaps, and next action

    Returns:
        Confirmation that reflection was recorded
    """
    return f"Reflection recorded: {reflection}" 
