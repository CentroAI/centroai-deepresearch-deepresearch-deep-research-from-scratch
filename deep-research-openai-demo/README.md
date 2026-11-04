# Deep Research Agent — classroom demo

A Flask chatbot UI wrapping the `full_agent` LangGraph pipeline
(`clarify_with_user → write_research_brief → run_research → final_report_generation`)
from `research_agent_full.py`, adapted to use **OpenAI (`gpt-4o-mini`)** instead of Groq.

The sidebar lights up each pipeline stage live as it runs, so students can see
the graph execute node by node instead of just waiting for a final answer.

## 1. Put this folder next to (not inside) your original course repo

See the PowerShell commands you were given separately for copying your
existing `src/deep_research_from_scratch` folder — this zip's `src/` only
contains the 4 files that actually needed to change
(`research_agent_scope.py`, `research_agent.py`, `research_agent_full.py`,
`utils.py`). Extract this zip into your **new** folder so it overwrites
those 4 and adds `app.py`, `templates/`, `static/`, `requirements.txt`.

## 2. Add your API keys

Copy `.env.example` to a new file named exactly `.env`, in the **same folder
as `app.py`** (the project root — NOT inside `src/`). Then open `.env` and
replace the placeholders:

```
OPENAI_API_KEY=sk-...your real key...
TAVILY_API_KEY=tvly-...your real key...
```

This file is only read locally by `app.py` (via `python-dotenv`) — it's
never sent anywhere, never shown in the browser, and students never see it.
Do not commit `.env` to git or share the folder as a zip with it inside.

## 3. Install dependencies

```powershell
cd path\to\this\folder
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 4. Run it

```powershell
python app.py
```

Then open **http://127.0.0.1:5000** in your browser (or project it for the
class). Each message you send streams live through the 4 pipeline stages
shown in the sidebar.

## Cost note

`gpt-4o-mini` is roughly $0.15 / 1M input tokens and $0.60 / 1M output
tokens. A full run (clarify + brief + 2-3 searches + report) typically
costs a few cents — a $5 balance covers dozens of full demo runs.

## Notes for the demo

- Each browser tab/session gets its own `thread_id` (shown nowhere in the
  UI, but it's what lets `clarify_with_user` remember earlier messages in
  the same conversation — exactly like the notebook's `InMemorySaver`).
- State lives only in RAM (`InMemorySaver`), same as in the notebooks —
  restarting `app.py` clears all conversations. That's fine for a demo.
- "+ New conversation" just grabs a fresh `thread_id`; it does not restart
  the Flask process.
- If a student-facing link is needed instead of a local-only demo, that
  requires actual deployment (not covered here) — don't just port-forward
  your dev machine with your personal API key attached, since port
  forwarding exposes the raw Flask app with no key protection.
