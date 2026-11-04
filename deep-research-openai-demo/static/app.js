const chatEl = document.getElementById("chat");
const formEl = document.getElementById("chat-form");
const inputEl = document.getElementById("chat-input");
const sendBtn = document.getElementById("send-btn");
const reportPanel = document.getElementById("report-panel");
const reportContent = document.getElementById("report-content");
const copyBtn = document.getElementById("copy-report-btn");
const newChatBtn = document.getElementById("new-chat-btn");

const STAGE_ORDER = ["clarify_with_user", "write_research_brief", "run_research", "final_report_generation"];

let threadId = null;

async function initThread() {
  const res = await fetch("/api/thread", { method: "POST" });
  const data = await res.json();
  threadId = data.thread_id;
}
initThread();

function addBubble(role, text) {
  const wrap = document.createElement("div");
  wrap.className = `msg ${role}`;
  const bubble = document.createElement("div");
  bubble.className = "msg-bubble";
  bubble.textContent = text;
  wrap.appendChild(bubble);
  chatEl.appendChild(wrap);
  chatEl.scrollTop = chatEl.scrollHeight;
  return bubble;
}

function addStatusBubble(label) {
  const wrap = document.createElement("div");
  wrap.className = "msg status";
  wrap.innerHTML = `<div class="msg-bubble"><span class="spinner"></span><span class="status-text">${label}…</span></div>`;
  chatEl.appendChild(wrap);
  chatEl.scrollTop = chatEl.scrollHeight;
  return wrap.querySelector(".status-text");
}

function setStage(stageName, state) {
  const idx = STAGE_ORDER.indexOf(stageName);
  if (idx === -1) return;
  STAGE_ORDER.slice(0, idx).forEach((s) => markStageEl(s, "done"));
  markStageEl(stageName, state);
}

function markStageEl(stageName, state) {
  const el = document.querySelector(`.stage[data-stage="${stageName}"]`);
  if (!el) return;
  el.classList.remove("active", "done");
  if (state) el.classList.add(state);
}

function resetStages() {
  STAGE_ORDER.forEach((s) => markStageEl(s, null));
}

function renderReport(markdown) {
  reportPanel.classList.remove("hidden");
  reportContent.innerHTML = marked.parse(markdown || "");
  reportContent.dataset.raw = markdown || "";
}

copyBtn.addEventListener("click", () => {
  navigator.clipboard.writeText(reportContent.dataset.raw || "");
  copyBtn.textContent = "Copied!";
  setTimeout(() => (copyBtn.textContent = "Copy"), 1200);
});

newChatBtn.addEventListener("click", async () => {
  chatEl.innerHTML = "";
  reportPanel.classList.add("hidden");
  reportContent.innerHTML = "";
  resetStages();
  addBubble("assistant", "New conversation started — what would you like researched?");
  await initThread();
});

formEl.addEventListener("submit", async (e) => {
  e.preventDefault();
  const message = inputEl.value.trim();
  if (!message) return;

  addBubble("user", message);
  inputEl.value = "";
  inputEl.disabled = true;
  sendBtn.disabled = true;

  // Tracks the single "in progress" status bubble across the whole stream.
  // It gets cleared and re-created as different stages fire, so the user
  // always sees exactly one live status line until a real answer appears.
  let statusEl = null;

  function ensureStatus(label) {
    if (!statusEl) {
      statusEl = addStatusBubble(label);
    } else {
      statusEl.textContent = `${label}…`;
    }
  }

  function clearStatus() {
    if (statusEl) {
      const wrap = statusEl.closest(".msg");
      if (wrap) wrap.remove();
      statusEl = null;
    }
  }

  ensureStatus("Thinking");

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, thread_id: threadId }),
    });

    if (!res.ok) {
      const errBody = await res.json().catch(() => ({}));
      throw new Error(errBody.error || `Request failed (${res.status})`);
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      const lines = buffer.split("\n");
      buffer = lines.pop(); // keep partial line for next chunk

      for (const line of lines) {
        if (!line.trim()) continue;
        const evt = JSON.parse(line);

        if (evt.stage === "done") {
          clearStatus();
          continue;
        }
        if (evt.stage === "error") {
          clearStatus();
          addBubble("assistant", `⚠️ ${evt.message}`);
          continue;
        }

        setStage(evt.stage, "active");

        if (evt.stage === "clarify_with_user" && evt.assistant_message) {
          clearStatus();
          addBubble("assistant", evt.assistant_message);
        } else if (evt.stage === "final_report_generation" && evt.final_report) {
          setStage(evt.stage, "done");
          clearStatus();
          addBubble("assistant", "Here's the final report 👇");
          renderReport(evt.final_report);
        } else {
          ensureStatus(evt.label || evt.stage);
        }
      }
    }
  } catch (err) {
    clearStatus();
    addBubble("assistant", `⚠️ Something went wrong: ${err.message}`);
  } finally {
    inputEl.disabled = false;
    sendBtn.disabled = false;
    inputEl.focus();
  }
});
