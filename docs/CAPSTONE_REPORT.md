# K0isec Guardian - Capstone Project Report

**Author:** Bismark Koima
**Project:** An offline AI cyber-safety assistant for older adults

> Sections marked **[TODO]** are for you to complete with your own data, sources and results
> (e.g. statistics with citations, user-testing feedback).

---

## 1. Problem statement

Older adults are frequent targets of fraud such as phishing emails and texts, fake tech-support calls,
"grandchild in trouble" calls, romance scams and demands for payment in gift cards. Many existing security
tools are built for technical users: they use jargon, small text and complex settings, and AI chatbots
usually send everything the user types to cloud servers - a privacy concern for people discussing their
finances and personal details.

**[TODO]** Add statistics on elder fraud in your country/region with citations
(for example from national police, fraud reporting centres or consumer protection agencies).

## 2. Aim and objectives

**Aim:** build an easy-to-use assistant that teaches older adults how to recognise and respond to scams,
while keeping their conversations completely private.

**Objectives**
1. Provide a conversational assistant that answers safety questions in plain, reassuring language.
2. Run the AI model **offline** on the user's own computer, so no data leaves the device.
3. Keep working even without an AI model, using a built-in safety guide.
4. Let users paste a suspicious message and get an explained risk rating.
5. Teach core skills through short lessons and quizzes.
6. Meet accessibility needs of older users (large text, high contrast, read-aloud, simple navigation).
7. Follow secure-development practice (no secrets in code, input validation, security headers, tests).

## 3. Target users

- Adults aged roughly 60+ with basic computer or tablet experience.
- Family members or carers who set the app up and want to help a relative stay safe.
- Community centres, libraries or churches running digital-skills sessions.

## 4. Requirements

### Functional
| ID | Requirement | Where implemented |
|---|---|---|
| F1 | Answer safety questions in a chat | `guardian/assistant.py`, `templates/index.html` |
| F2 | Use a local, offline LLM | `guardian/llm.py` (Ollama) |
| F3 | Fall back to a built-in guide when no model is available | `guardian/knowledge.py` |
| F4 | Analyse a pasted message for scam warning signs | `guardian/scam_checker.py`, `/check` |
| F5 | Lessons with quizzes and progress | `guardian/lessons.py`, `static/lessons.js` |
| F6 | Emergency "I've been scammed" guidance | `templates/help.html` |
| F7 | Quick topic buttons for common scams | `templates/index.html` |

### Non-functional
| ID | Requirement | How it is met |
|---|---|---|
| N1 | Privacy | Offline model; server bound to `127.0.0.1`; no logging or storing of messages; personal numbers kept only in the browser |
| N2 | Accessibility | Large 20px text by default, 3 text sizes (16/20/24px), high contrast, dark mode, ≥44px tap targets, focus outlines, skip link, ARIA live regions, read-aloud |
| N3 | Works on ordinary hardware | Small 2-4B parameter models; guide-only mode needs no model at all |
| N4 | Security | Strict Content-Security-Policy, no inline scripts, `textContent` only (no HTML injection), input length limits, request size limit, no secrets in the repository |
| N5 | Reliability | Every chat request returns an answer, even if the model fails |
| N6 | Maintainability | Small modules, automated tests, CI on GitHub Actions |

## 5. System design

### Architecture

```
Browser UI ──HTTP──► Flask (app.py)
                       ├─ Assistant ──► OfflineLLM ──► Ollama (local model)
                       │       └──────► Knowledge base (fallback + reference notes)
                       ├─ Scam checker (rules + link analysis)
                       └─ Lessons
```

### Key design decisions

**Offline LLM via Ollama.** Ollama packages open models (Llama 3.2, Phi-3, Gemma 2, Qwen 2.5) behind a
simple local HTTP API. The client uses only the Python standard library, keeping dependencies minimal.
The default model, `llama3.2:3b`, is small enough for an ordinary laptop.

**Retrieval of trusted notes.** Small models can make mistakes, so before calling the model the assistant
finds matching topics in the hand-written safety guide and runs the scam checker on the question. These are
passed to the model as reference material, grounding its answers in vetted advice.

**Graceful fallback.** If Ollama is not installed, the model isn't downloaded, or a request fails/times out,
the user still gets a useful answer from the guide. The footer shows which mode is in use.

**Explainable scam checker.** Rather than a black-box score, the checker uses transparent rules (urgency,
threats, requests for codes/passwords, unusual payment methods, secrecy, "hi mum" messages, remote-access
requests, fake deliveries) and link analysis (shorteners, IP-address links, unusual domain endings,
look-alike brand domains, punycode). Each warning is explained in plain words, so every check is also a
small lesson. Requests for codes, gift-card/crypto payments, or remote access are always rated high risk.

**Prompt design.** The system prompt asks for short answers, plain words, a warm tone, numbered steps,
never requesting private details, staying on topic, and admitting uncertainty. Only `user`/`assistant`
turns are accepted from the browser's history, so a client cannot inject extra system instructions.

## 6. Implementation

- **Language/framework:** Python 3, Flask, Jinja2, vanilla JavaScript, CSS.
- **AI runtime:** Ollama (any compatible local model).
- **Testing:** `unittest`-style tests run with pytest; GitHub Actions CI.

Screenshots:

| Home / chat | Lesson & quiz |
|---|---|
| ![Home](screenshots/home.png) | ![Lesson](screenshots/lesson.png) |

## 7. Testing and evaluation

### Automated tests (26 tests)
- **Scam checker:** phishing email, "hi mum" gift-card message, code requests, remote access,
  harmless message, real vs. look-alike domains, link shorteners, empty/huge input.
- **Knowledge base:** topic matching for typical questions, fallback answer, valid quiz answers.
- **Assistant:** uses the model when available, passes reference notes, filters/trims history,
  falls back when the model is missing or errors.
- **Web app:** every page loads with security headers, 404 handling, API validation.

### Suggested user evaluation **[TODO]**
1. Recruit 5-10 older adults (with consent).
2. Ask each to complete tasks: ask a question, check three sample messages (two scams, one genuine),
   complete one lesson.
3. Measure task completion, time taken, quiz scores, and a System Usability Scale (SUS) questionnaire.
4. Record feedback on text size, wording and the read-aloud feature.

### Suggested model comparison **[TODO]**
Ask the same 10 questions to 2-3 local models (e.g. `llama3.2:3b`, `phi3:mini`, `gemma2:2b`) and rate
answers for accuracy, simplicity and response time on your hardware.

## 8. Limitations

- Rule-based detection can miss new scam wording and may flag some genuine messages.
- Small local models can still be wrong; answers are grounded but not guaranteed.
- Voice input depends on the browser and may use an online speech service in some browsers.
- Content is currently English-only.

## 9. Future work

- Additional languages (e.g. Swahili) and region-specific reporting contacts.
- Screenshot/photo upload with offline OCR to check messages from a phone.
- Fully offline speech recognition (e.g. Whisper running locally).
- Packaging as a one-click desktop installer for non-technical users.
- A "trusted contact" mode to share a check result with a family member.

## 10. Ethics and privacy

- No personal data is collected, stored on a server, or sent to third parties.
- The app gives educational guidance only and tells users to contact their bank and the police when money
  is involved.
- Language is respectful and avoids blaming victims.

## 11. Conclusion **[TODO]**

Summarise what was achieved against each objective, what you learned, and the results of your evaluation.

## References **[TODO]**

Add the sources you used (fraud statistics, accessibility guidelines such as WCAG 2.2, Ollama documentation,
model cards for the models you tested).
