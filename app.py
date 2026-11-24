import os
import json
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
import google.generativeai as genai

app = Flask(__name__)

# Configure Gemini API
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

SYSTEM_INSTRUCTION = """# AI Business Build Helper

Help create the Career Venture Lab business simulator using prompts from the project and student guides, and guide one-at-a-time testing of each AI component outside the dashboard. Explain modules in plain, everyday layman's terms and pinpoint where to find every input, including which dashboard mode or module holds it.

## Build Workflow
1. Gather or confirm the team's course, career pathway, team ID, and approved challenge level before generating build or role prompts.
2. Assemble prompts in the handbook's required order: common operating or build instructions, course adapter, pathway card, business package rules, and approved snapshot data.
3. Keep human review and approval in the loop before advancing simulation state or releasing assessments.
4. Explain modules in plain layman's terms whenever describing a simulator module, feature, or business function, avoiding unexplained jargon.

## Comprehensive AI Component Testing Workflow
When the user requests a comprehensive test of the business's AI components, guide testing outside the dashboard one component at a time:
1. Create a testing checklist: Identify every AI component, skill, or Gem supporting the business (Finance, Operations, Market and Marketing, Independent Reviewer) and list each component separately.
2. Explain each component before testing: State its purpose, the business function it supports in plain layman's terms, and the expected outputs before running its test.
3. Help locate inputs: Identify where to find inputs for business functionality components. List the required inputs for that component, specify the exact dashboard app mode or module where each input lives (or note if it comes from a snapshot file, guide, or sample/simulated data), show how to enter it, and clearly label any sample or simulated data.
4. Provide a specific test: Give the exact test prompt or instructions, expected outputs, and clear pass/fail criteria for the component.
5. Test one component at a time: Wait for the user to review the current component's results before moving to the next.
6. Evaluate and record results: Maintain a testing log containing:
   - Component name and test date.
   - Inputs used and expected outputs.
   - Actual results and supporting evidence.
   - Status: Not Started, In Progress, Passed, Failed, or Blocked.
   - Problems identified and any corrections or retesting needed.
7. Strict pass rule: Mark a test Passed only when observed results meet the defined success criteria.
8. Track remaining work: After each test, summarize what passed, what needs attention, and which tests remain, then recommend the next component to test.
9. Support resuming later: At the end of each session, provide a saveable updated testing log to supply when resuming, and include a final check of how components exchange information once individual tests are complete.

## Strict Rules
- Never skip ahead to a second component before reviewing the current component's results.
- Never mark a test Passed if expected criteria were not met or if results are missing.
- Clearly distinguish sample or simulated fixture data from live or approved snapshot records.
- Always translate module and technical terms into plain layman's terms and name the exact dashboard mode or module where inputs are found.
"""

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Career Venture Lab — AI Business Build Helper</title>
    <style>
        :root {
            --bg: #f4f7f9;
            --card: #ffffff;
            --primary: #1e3a8a;
            --primary-hover: #1d4ed8;
            --accent: #0f766e;
            --border: #d1d5db;
            --text: #1f2937;
            --muted: #6b7280;
        }
        * { box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background: var(--bg);
            color: var(--text);
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }
        header {
            background: var(--primary);
            color: #fff;
            padding: 1rem 1.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        header h1 { margin: 0; font-size: 1.25rem; }
        header span { font-size: 0.85rem; opacity: 0.9; }
        .container {
            display: grid;
            grid-template-columns: 320px 1fr;
            gap: 1.25rem;
            padding: 1.25rem;
            max-width: 1400px;
            width: 100%;
            margin: 0 auto;
            flex: 1;
        }
        @media (max-width: 900px) {
            .container { grid-template-columns: 1fr; }
        }
        .panel {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1rem;
            display: flex;
            flex-direction: column;
            gap: 0.85rem;
        }
        .panel h2 {
            margin: 0 0 0.25rem 0;
            font-size: 1rem;
            color: var(--primary);
            border-bottom: 1px solid var(--border);
            padding-bottom: 0.5rem;
        }
        label {
            display: block;
            font-size: 0.8rem;
            font-weight: 600;
            margin-bottom: 0.25rem;
            color: var(--text);
        }
        input, select, textarea {
            width: 100%;
            padding: 0.5rem;
            border: 1px solid var(--border);
            border-radius: 6px;
            font-size: 0.9rem;
            font-family: inherit;
        }
        button {
            background: var(--primary);
            color: white;
            border: none;
            padding: 0.6rem 1rem;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            font-size: 0.9rem;
            transition: background 0.15s;
        }
        button:hover { background: var(--primary-hover); }
        button:disabled { background: var(--muted); cursor: not-allowed; }
        button.secondary {
            background: var(--accent);
        }
        button.outline {
            background: transparent;
            color: var(--primary);
            border: 1px solid var(--primary);
        }
        .chat-box {
            flex: 1;
            min-height: 420px;
            max-height: 62vh;
            overflow-y: auto;
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 1rem;
            background: #fafafa;
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }
        .msg {
            padding: 0.75rem 1rem;
            border-radius: 8px;
            max-width: 88%;
            line-height: 1.5;
            white-space: pre-wrap;
            font-size: 0.92rem;
        }
        .msg.user {
            background: var(--primary);
            color: #fff;
            align-self: flex-end;
        }
        .msg.assistant {
            background: #ffffff;
            border: 1px solid var(--border);
            align-self: flex-start;
        }
        .input-row {
            display: flex;
            gap: 0.5rem;
        }
        .input-row textarea {
            resize: vertical;
            min-height: 52px;
        }
        .quick-actions {
            display: flex;
            flex-wrap: wrap;
            gap: 0.4rem;
        }
        .quick-actions button {
            font-size: 0.78rem;
            padding: 0.4rem 0.65rem;
        }
        .status-badge {
            font-size: 0.78rem;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            background: #e0f2fe;
            color: #0369a1;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <header>
        <div>
            <h1>Career Venture Lab — AI Business Build Helper</h1>
            <span>Simulator Prompt Staging & One-at-a-Time Component Testing</span>
        </div>
        <div class="status-badge" id="apiStatus">Ready</div>
    </header>

    <div class="container">
        <aside class="panel">
            <h2>Team & Simulator Context</h2>
            <div>
                <label for="course">Course</label>
                <input type="text" id="course" placeholder="e.g., Entrepreneurship / AP Stats">
            </div>
            <div>
                <label for="pathway">Career Pathway</label>
                <input type="text" id="pathway" placeholder="e.g., Business Management & Finance">
            </div>
            <div>
                <label for="teamId">Team ID</label>
                <input type="text" id="teamId" placeholder="e.g., TEAM-04">
            </div>
            <div>
                <label for="challengeLevel">Approved Challenge Level</label>
                <select id="challengeLevel">
                    <option value="Level 1 (Guided)">Level 1 (Guided)</option>
                    <option value="Level 2 (Standard)" selected>Level 2 (Standard)</option>
                    <option value="Level 3 (Advanced)">Level 3 (Advanced)</option>
                </select>
            </div>
            <div>
                <label for="testingLog">Saved Testing Log (Optional Resume)</label>
                <textarea id="testingLog" rows="4" placeholder="Paste prior testing log JSON or notes here to resume..."></textarea>
            </div>
            <button class="secondary" onclick="exportLog()">Download Session Log (.txt)</button>
            <button class="outline" onclick="clearChat()">Reset Conversation</button>
        </aside>

        <main class="panel">
            <h2>Build & Component Testing Workspace</h2>
            <div class="quick-actions">
                <button class="outline" onclick="sendQuick('Start Build Workflow: confirm our team setup and assemble prompts in required order.')">1. Stage Build Prompts</button>
                <button class="outline" onclick="sendQuick('Start Comprehensive AI Component Testing: create our testing checklist and begin with the first component only.')">2. Start Component Testing</button>
                <button class="outline" onclick="sendQuick('Explain all simulator modules and where to find every input in plain layman terms.')">3. Module & Input Map</button>
                <button class="outline" onclick="sendQuick('Generate our updated saveable Testing Log summary so we can resume later.')">4. Saveable Testing Log</button>
            </div>

            <div class="chat-box" id="chatBox">
                <div class="msg assistant">Welcome to the Career Venture Lab AI Business Build Helper!

Fill in your team details on the left (Course, Career Pathway, Team ID, and Challenge Level), then choose a quick action above or ask a question below to:
• Assemble simulator prompts in the required handbook order
• Locate inputs across dashboard modes/modules in plain everyday terms
• Run step-by-step, one-at-a-time tests for Finance, Operations, Market & Marketing, and Independent Reviewer components.</div>
            </div>

            <div class="input-row">
                <textarea id="userInput" placeholder="Type your message, paste component test output for evaluation, or ask where to find an input..."></textarea>
                <button id="sendBtn" onclick="sendMessage()">Send</button>
            </div>
        </main>
    </div>

    <script>
        let history = [];

        function appendMessage(role, text) {
            const box = document.getElementById('chatBox');
            const div = document.createElement('div');
            div.className = 'msg ' + role;
            div.textContent = text;
            box.appendChild(div);
            box.scrollTop = box.scrollHeight;
        }

        function sendQuick(text) {
            document.getElementById('userInput').value = text;
            sendMessage();
        }

        async function sendMessage() {
            const inputEl = document.getElementById('userInput');
            const sendBtn = document.getElementById('sendBtn');
            const statusEl = document.getElementById('apiStatus');
            const message = inputEl.value.trim();
            if (!message) return;

            const context = {
                course: document.getElementById('course').value.trim(),
                pathway: document.getElementById('pathway').value.trim(),
                team_id: document.getElementById('teamId').value.trim(),
                challenge_level: document.getElementById('challengeLevel').value,
                testing_log: document.getElementById('testingLog').value.trim()
            };

            appendMessage('user', message);
            inputEl.value = '';
            sendBtn.disabled = true;
            statusEl.textContent = 'Thinking...';

            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 55000);

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message, history, context }),
                    signal: controller.signal
                });
                clearTimeout(timeoutId);

                const data = await res.json();
                if (!res.ok) {
                    appendMessage('assistant', 'Error: ' + (data.error || 'Server returned an error.'));
                } else {
                    appendMessage('assistant', data.reply);
                    history.push({ role: 'user', text: message });
                    history.push({ role: 'model', text: data.reply });
                }
            } catch (err) {
                clearTimeout(timeoutId);
                if (err.name === 'AbortError') {
                    appendMessage('assistant', 'Request timed out before Render closed the connection. Please try a shorter prompt or retry.');
                } else {
                    appendMessage('assistant', 'Network error: ' + err.message);
                }
            } finally {
                sendBtn.disabled = false;
                statusEl.textContent = 'Ready';
            }
        }

        function clearChat() {
            history = [];
            document.getElementById('chatBox').innerHTML = '<div class="msg assistant">Conversation reset. Ready when you are!</div>';
        }

        function exportLog() {
            const lines = history.map(m => `[${m.role.toUpperCase()}]\n${m.text}\n`).join('\n---\n\n');
            const blob = new Blob([lines || 'No session messages yet.'], { type: 'text/plain' });
            const a = document.createElement('a');
            a.href = URL.createObjectURL(blob);
            a.download = `cvl_build_helper_log_${new Date().toISOString().slice(0,10)}.txt`;
            a.click();
        }

        document.getElementById('userInput').addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    </script>
</body>
</html>
"""

@app.route("/health")
def health():
    return jsonify({"status": "ok", "timestamp": datetime.utcnow().isoformat()}), 200

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/api/chat", methods=["POST"])
def chat():
    if not GEMINI_API_KEY:
        return jsonify({
            "error": "GEMINI_API_KEY is not set in Render Environment Variables. Add GEMINI_API_KEY and redeploy."
        }), 500

    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()
    history = data.get("history") or []
    context = data.get("context") or {}

    if not user_message:
        return jsonify({"error": "Message cannot be empty."}), 400

    context_block = (
        f"Current Team Context:\n"
        f"- Course: {context.get('course') or 'Not specified yet'}\n"
        f"- Career Pathway: {context.get('pathway') or 'Not specified yet'}\n"
        f"- Team ID: {context.get('team_id') or 'Not specified yet'}\n"
        f"- Approved Challenge Level: {context.get('challenge_level') or 'Not specified yet'}\n"
    )
    if context.get("testing_log"):
        context_block += f"- Prior Testing Log:\n{context.get('testing_log')}\n"

    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=SYSTEM_INSTRUCTION + "\n\n" + context_block
        )

        formatted_history = []
        for item in history[-12:]:
            role = "user" if item.get("role") == "user" else "model"
            formatted_history.append({"role": role, "parts": [item.get("text", "")]})

        chat_session = model.start_chat(history=formatted_history)
        response = chat_session.send_message(
            user_message,
            request_options={"timeout": 45}
        )
        return jsonify({"reply": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
