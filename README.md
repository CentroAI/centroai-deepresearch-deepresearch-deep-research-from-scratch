# 🧱 AI Agents and Deep Research — UVa / CentroAI Course

A hands-on two-day course on AI agents, organized in two blocks:

1. **Agent fundamentals** (notebooks `0` and `1`) — your first agent with LangChain, tools, conversation memory, and migration to LangGraph with state graphs.
2. **Deep Research from scratch** (notebooks `2`, `3` and `4`) — progressively building a deep research agent inspired by [open_deep_research](https://github.com/langchain-ai/open_deep_research).

Deep research has become one of the most popular agent applications: [OpenAI](https://openai.com/index/introducing-deep-research/), [Anthropic](https://www.anthropic.com/engineering/built-multi-agent-research-system), [Perplexity](https://www.perplexity.ai/hub/blog/introducing-perplexity-deep-research), and [Google](https://gemini.google/overview/deep-research/?hl=en) all have their own product of this kind. In this course we build a simplified version, step by step, to understand how it works under the hood.

## 🚀 Quickstart with GitHub Codespaces (recommended)

The easiest way to follow the course is using **GitHub Codespaces**, which automatically sets up the entire environment (Python, `uv`, dependencies, and the Jupyter kernel) without installing anything on your machine.

### Steps

1. Go to the repository: [centroai-deepresearch-deepresearch-deep-research-from-scratch](https://github.com/CentroAI/centroai-deepresearch-deepresearch-deep-research-from-scratch)
2. Click the green **`<> Code`** button → **Codespaces** tab → **Create codespace on main**.
3. Wait for provisioning to finish (1–3 minutes). The `.devcontainer/setup.sh` script runs automatically and:
   - Installs `uv`
   - Creates the virtual environment (`.venv`, Python 3.11)
   - Installs all project dependencies (`uv pip install -e ".[dev]"`)
   - Registers the Jupyter kernel **`Python (deep-research)`**
4. Once the Codespace is ready, open the `notebooks/` folder from the file explorer.
5. Open the first notebook (`0_AgentesIA_UVa_I_Agente_Simple_Langchain.ipynb`) and select the **`Python (deep-research)`** kernel (top right) if it isn't selected automatically.
6. Enter your API keys in the corresponding cell of each notebook (see [Required API keys](#-required-api-keys)) and run the cells in order.

You don't need to clone the repository, install Python, or configure `uv` manually — Codespaces does it all for you.

---

## 💻 Alternative: running locally

If you'd rather work on your own machine instead of Codespaces, follow these steps.

### Prerequisites

- **Python 3.11 or later** (required for LangGraph compatibility):
```bash
python3 --version
```

- **[uv](https://docs.astral.sh/uv/)** as the package and environment manager:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# Update your PATH to use the new uv installation
export PATH="$HOME/.local/bin:$PATH"
uv --version
```

### Installation

1. Clone the repository:
```bash
git clone https://github.com/CentroAI/centroai-deepresearch-deepresearch-deep-research-from-scratch.git
cd centroai-deepresearch-deepresearch-deep-research-from-scratch
```

2. Install the package and all dependencies (this automatically creates and manages the virtual environment in `.venv`):
```bash
uv sync
```

3. Register the Jupyter kernel so it shows up as an option in the notebooks:
```bash
uv run python -m ipykernel install --user --name deep-research --display-name "Python (deep-research)"
```

4. Launch Jupyter:
```bash
uv run jupyter notebook
# or, activating the virtual environment instead:
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
jupyter notebook
```

5. Open the notebooks from the `notebooks/` folder, select the **`Python (deep-research)`** kernel, and follow the same order as in Codespaces.

> ℹ️ API keys are **not** managed through a `.env` file: each notebook has its own setup cell at the top where you paste your keys directly (see next section).

---

## 🔑 Required API keys

Each notebook indicates which keys it needs in its first runnable cell. Summary:

| Notebooks | Service | Where to get it | Needed for |
|---|---|---|---|
| `0`, `1` | Hugging Face (`HUGGINGFACEHUB_API_TOKEN`) | [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) | LLM model (Qwen3 via Hugging Face Inference) |
| `2`, `3`, `4` | Groq (`GROQ_API_KEY`) | [console.groq.com](https://console.groq.com) (free) | LLM model for the research agents |
| `3`, `4` | Tavily (`TAVILY_API_KEY`) | [app.tavily.com](https://app.tavily.com) (free, 1,000 credits/month, no credit card) | Web search for the research agent |
| `2`, `3`, `4` (optional) | LangSmith (`LANGSMITH_API_KEY`) | [smith.langchain.com](https://smith.langchain.com/) | Tracing and debugging the graphs (optional but recommended) |

All keys are entered directly in the configuration cell of each notebook — no `.env` file is required.

---

## 📝 Course organization

### 📚 Block 1 — Agent fundamentals

#### `0_AgentesIA_UVa_I_Agente_Simple_Langchain.ipynb`
**Purpose**: Build your first AI agent with LangChain and understand the difference between a plain LLM and an agent.

**Key concepts**:
- Setting up API keys and libraries
- The **Tool Use** pattern: defining tools with the `@tool` decorator
- Wiring up the LLM as the agent's "engine"
- Managing conversation history (memory)
- Filtering and formatting the agent's output

**Includes 2 hands-on exercises**: implementing a city weather lookup tool and a temperature conversion tool (°C → °F).

---

#### `1_AgentesIA_UVa_II_Agentes_LangGraph.ipynb`
**Purpose**: Migrate from a simple agent to a state graph with LangGraph.

**Key concepts**:
- Defining the graph's **state**
- Building **nodes** and edges
- Generating chatbot responses inside the graph
- Visualizing the graph
- Integrating an external tool (Wikipedia) as a graph node
- Dynamically modifying the graph's flow and recompiling it

---

### 🔬 Block 2 — Deep Research from scratch

#### `2_scoping.ipynb` — User clarification and research brief generation
**Purpose**: Turn an ambiguous user request into a structured research brief.

**Key concepts**:
- **Structured output**: Pydantic schemas (`ClarifyWithUser`, `ResearchQuestion`) to force reliable LLM responses and prevent hallucination
- **Shared state**: how information travels between graph nodes
- **LangGraph commands** (`Command`) for flow control and state updates
- Conditional routing based on whether clarification is needed
- Date-aware prompts

**Includes 4 exercises**, including defining your own structured output schema and testing multi-turn conversations.

---

#### `3_research_agent.ipynb` — Research agent with tools
**Purpose**: Build an iterative research agent with real web search.

**Key concepts**:
- Agent architecture: LLM decision node + tool execution node (ReAct pattern)
- Tools: `tavily_search` (web search with content summarization) and `think_tool` (mandatory reflection between steps)
- `InjectedToolArg` to hide internal arguments from the LLM
- Compressing research results (`compress_research`)
- Conditional routing (`should_continue`) to decide when to keep searching or stop

**Includes 5 exercises**, including modifying the agent's prompt, inspecting what the LLM actually sees, and manually tracing the routing logic.

---

#### `4_full_agent.ipynb` — Full research agent (end-to-end)
**Purpose**: Integrate everything above into a complete system: Scope → Research → Write.

**Key concepts**:
- A bridge node connecting the scoping phase to the research phase
- Final report generation prompt and node (`final_report_generation`)
- Subgraph composition and state management across all phases
- The complete end-to-end flow: from the initial user request to the final report

**Includes 5 exercises**, culminating in running the full pipeline on a topic of the student's own choosing.

---

### 🎯 Learning outcomes

- **Agents with LangChain**: tools, conversational memory, the Tool Use pattern
- **Agents with LangGraph**: state, nodes, edges, compilable and visualizable graphs
- **Structured output**: Pydantic schemas for reliable LLM decisions
- **Agent patterns**: ReAct loops, reflection with `think_tool`, conditional routing
- **Search integration**: Tavily as an external information source
- **Research workflow design**: scoping → research → final report writing
- **State management**: complex state flow across multiple phases and subgraphs

Each notebook builds on the concepts from the previous one, culminating in a working deep research system capable of clarifying an ambiguous request, autonomously researching with real web search, and producing a coherent final report.
