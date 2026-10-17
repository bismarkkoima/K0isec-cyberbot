# K0isec Guardian 🛡️

**An offline cyber-safety assistant that helps older adults recognise scams and stay safe online.**

K0isec Guardian is a friendly chatbot, scam-message checker and set of bite-sized lessons designed
for people who are less confident with technology. It runs a **local, offline large language model**
(via [Ollama](https://ollama.com)), so nothing a user types ever leaves their computer - and if no model
is installed it still answers from a built-in, plain-language safety guide.

![Home screen](docs/screenshots/home.png)

## Features

| | Feature | What it does |
|---|---|---|
| 💬 | **Ask a question** | Chat with an offline AI that answers in simple, reassuring language. |
| 🔍 | **Check a message** | Paste a text, email or what a caller said; the checker highlights scam warning signs and explains each one. |
| 📘 | **Lessons & quizzes** | Four 3-4 minute lessons with quick quizzes that remember what you've completed. |
| 🆘 | **I think I've been scammed** | Calm, step-by-step emergency guide plus a private card for important phone numbers. |
| 🔤 | **Accessibility** | Large text by default, A / A+ / A++ sizes, high contrast, dark mode, big buttons, keyboard friendly. |
| 🔊 | **Read aloud & speak** | Answers and lessons can be read out loud; voice input where the browser supports it. |
| 🔒 | **Private by design** | No cloud APIs, no accounts, no tracking. Binds to `127.0.0.1` only. |

## How it works

```
 Browser (large-text UI)
        │  fetch /api/chat, /api/check
        ▼
 Flask app (app.py)
        │
        ├── guardian/assistant.py ──► guardian/llm.py ──► Ollama on this computer (e.g. llama3.2:3b)
        │        │                         (offline LLM)
        │        └─ if model missing/fails ─► guardian/knowledge.py (built-in safety guide)
        │
        ├── guardian/scam_checker.py  (rule-based warning-sign detector)
        └── guardian/lessons.py       (lessons + quizzes)
```

When a question arrives, the assistant:
1. Finds the most relevant topics in the built-in safety guide and runs the scam checker on the question.
2. Sends these as *trusted reference notes* together with an elderly-friendly system prompt to the local model.
3. If the model isn't installed, isn't running, or errors, it answers directly from the safety guide instead.

The footer shows which mode is active (🟢 offline AI ready / 🟡 using the built-in guide).

## Getting started

### 1. Install the app

Requires Python 3.10+.

```bash
git clone https://github.com/bismarkkoima/k0isec-cyberbot.git
cd k0isec-cyberbot
python -m venv .venv
# Windows: .venv\Scripts\activate     macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # optional - defaults work out of the box
```

### 2. Install the offline AI model (optional but recommended)

1. Download and install Ollama from <https://ollama.com/download>.
2. Pull a small model (about 2 GB, done once while online):

   ```bash
   ollama pull llama3.2:3b
   ```

   Other good small models: `phi3:mini`, `gemma2:2b`, `qwen2.5:3b`. Set `OLLAMA_MODEL` in `.env` to switch.

After this the computer can be disconnected from the internet - everything runs locally.

### 3. Run it

```bash
python app.py
```

Open <http://127.0.0.1:5000> in a web browser.

## Configuration (`.env`)

| Variable | Default | Purpose |
|---|---|---|
| `OLLAMA_HOST` | `http://localhost:11434` | Address of the local Ollama server |
| `OLLAMA_MODEL` | `llama3.2:3b` | Model used for chat answers |
| `OLLAMA_TIMEOUT` | `60` | Seconds to wait before falling back to the guide |
| `FLASK_DEBUG` | `0` | Set to `1` only while developing |
| `PORT` | `5000` | Port for the web server |

## Running the tests

```bash
pip install -r requirements-dev.txt
pytest -q
```

The tests use a fake model, so they don't need Ollama. They also run automatically on GitHub Actions.

## Project structure

```
app.py                  Flask routes, API and security headers
guardian/
  assistant.py          Chat logic: offline LLM + fallback
  llm.py                Ollama client (standard library only)
  knowledge.py          Built-in plain-language safety guide
  scam_checker.py       Rule-based scam warning-sign detector
  lessons.py            Lessons and quiz questions
templates/              Jinja2 pages
static/                 CSS and JavaScript (no inline scripts)
tests/                  Unit and route tests
docs/CAPSTONE_REPORT.md Capstone write-up
```

## Capstone documentation

See [docs/CAPSTONE_REPORT.md](docs/CAPSTONE_REPORT.md) for the problem statement, objectives,
design decisions, evaluation and future work.

## Disclaimer

K0isec Guardian gives general safety education. It can't guarantee that a message is safe or a scam.
If you have lost money, contact your bank and the police straight away.

---
© 2025-2026 Bismark Koima · K0isec Cyber Sentinel
