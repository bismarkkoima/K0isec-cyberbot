"""The chat assistant: offline LLM first, built-in guide as a fallback."""

from . import knowledge, scam_checker
from .llm import OfflineLLM

SYSTEM_PROMPT = """You are K0isec Guardian, a patient and kind cyber-safety helper for older adults.

How to answer:
- Use simple, everyday words. Explain any technical word you must use.
- Keep answers short: a friendly sentence, then at most 5 numbered steps.
- Be warm and reassuring. Never make the person feel foolish; scams fool clever people too.
- If something sounds like a scam, say so clearly and tell them what to do next.
- Always recommend checking with the real organisation using contact details they already trust,
  and talking to a trusted family member or friend.
- Never ask for passwords, PINs, codes, card numbers or other private details.
- Only help with staying safe online, on the phone and with money. Politely steer other topics back.
- If you are not sure, say so rather than guessing."""

MAX_HISTORY = 8
MAX_MESSAGE_LENGTH = 2000


class Assistant:
    def __init__(self, llm=None):
        self.llm = llm or OfflineLLM()

    def _reference(self, message):
        """Build trusted reference notes for the model from the built-in guide."""
        notes = [f"{t['title']}:\n{t['answer']}" for t in knowledge.search(message)]
        check = scam_checker.analyze(message)
        if check["level"] != "low":
            signs = ", ".join(f["title"].lower() for f in check["flags"])
            notes.append(f"Automatic scam check of the user's message: {check['level']} risk ({signs}).")
        return "\n\n".join(notes)

    def reply(self, message, history=None):
        """Return {"reply": str, "source": "offline-llm" | "safety-guide"}."""
        message = (message or "").strip()[:MAX_MESSAGE_LENGTH]
        if not message:
            return {"reply": "Please type a question and I'll do my best to help.", "source": "safety-guide"}

        if self.llm.is_available():
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            reference = self._reference(message)
            if reference:
                messages.append({"role": "system",
                                 "content": "Trusted reference notes (use if relevant):\n\n" + reference})
            for turn in (history or [])[-MAX_HISTORY:]:
                role = turn.get("role")
                content = str(turn.get("content", ""))[:MAX_MESSAGE_LENGTH]
                if role in ("user", "assistant") and content:
                    messages.append({"role": role, "content": content})
            messages.append({"role": "user", "content": message})
            try:
                return {"reply": self.llm.chat(messages), "source": "offline-llm"}
            except RuntimeError:
                pass  # fall through to the built-in guide

        return {"reply": knowledge.answer(message), "source": "safety-guide"}
