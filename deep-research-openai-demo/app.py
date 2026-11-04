"""
Deep Research Agent — classroom demo
=====================================
A small Flask app that wraps the full_agent graph (clarify -> brief ->
research -> report) from research_agent_full.py and streams each pipeline
stage to the browser live, so students can see the LangGraph nodes fire
in real time instead of just waiting for one final answer.

Run with:   python app.py
Then open:  http://127.0.0.1:5000
"""

import os
import sys
import json
import uuid

from flask import Flask, Response, request, render_template, stream_with_context
from dotenv import load_dotenv

# ── Make the course's src/ package importable without an editable install ──
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

# ── Load OPENAI_API_KEY / TAVILY_API_KEY from .env (see .env.example) ──────
load_dotenv()

from langchain_core.messages import HumanMessage  # noqa: E402
from deep_research_from_scratch.research_agent_full import full_agent  # noqa: E402

app = Flask(__name__)

# Friendly labels shown in the UI for each graph node
STAGE_LABELS = {
    "clarify_with_user":       "Clarifying",
    "write_research_brief":    "Writing research brief",
    "run_research":            "Researching the web",
    "final_report_generation": "Writing the final report",
}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/thread", methods=["POST"])
def new_thread():
    """Issue a fresh thread_id — one per conversation / browser tab."""
    return {"thread_id": str(uuid.uuid4())}


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    user_message = (data or {}).get("message", "").strip()
    thread_id = (data or {}).get("thread_id") or str(uuid.uuid4())

    if not user_message:
        return {"error": "empty message"}, 400

    config = {"configurable": {"thread_id": thread_id}}

    def generate():
        try:
            for chunk in full_agent.stream(
                {"messages": [HumanMessage(content=user_message)]},
                config=config,
                stream_mode="updates",
            ):
                node_name = next(iter(chunk))
                node_data = chunk[node_name] or {}

                payload = {
                    "stage": node_name,
                    "label": STAGE_LABELS.get(node_name, node_name),
                }

                if node_name == "clarify_with_user":
                    msgs = node_data.get("messages", [])
                    if msgs:
                        payload["assistant_message"] = msgs[-1].content

                elif node_name == "write_research_brief":
                    payload["research_brief"] = node_data.get("research_brief", "")

                elif node_name == "run_research":
                    notes = node_data.get("notes", [])
                    payload["notes_preview"] = (notes[0][:400] + "…") if notes else ""

                elif node_name == "final_report_generation":
                    payload["final_report"] = node_data.get("final_report", "")
                    msgs = node_data.get("messages", [])
                    if msgs:
                        payload["assistant_message"] = "Here is your final report."

                yield json.dumps(payload) + "\n"

            yield json.dumps({"stage": "done"}) + "\n"

        except Exception as exc:  # surface errors to the UI instead of a silent hang
            yield json.dumps({"stage": "error", "message": str(exc)}) + "\n"

    return Response(stream_with_context(generate()), mimetype="application/x-ndjson")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
