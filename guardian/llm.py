"""Client for a local, offline large language model served by Ollama.

Ollama (https://ollama.com) runs open models such as Llama 3.2, Phi-3 or
Gemma entirely on the user's own computer. Nothing typed into K0isec Guardian
is sent to the internet. Only the Python standard library is used here so the
project has no extra dependencies.
"""

import json
import os
import time
import urllib.error
import urllib.request

DEFAULT_HOST = "http://localhost:11434"
DEFAULT_MODEL = "llama3.2:3b"


class OfflineLLM:
    """Small wrapper around the Ollama HTTP API (`/api/chat`, `/api/tags`)."""

    # How long a successful/failed availability check is trusted, in seconds
    STATUS_TTL = 30

    def __init__(self, host=None, model=None, timeout=None):
        self.host = (host or os.getenv("OLLAMA_HOST") or DEFAULT_HOST).rstrip("/")
        self.model = model or os.getenv("OLLAMA_MODEL") or DEFAULT_MODEL
        self.timeout = float(timeout or os.getenv("OLLAMA_TIMEOUT") or 60)
        self._status = None
        self._status_checked = 0.0

    def _request(self, path, payload=None, timeout=None):
        data = None
        headers = {}
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(self.host + path, data=data, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout or self.timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def status(self, force=False):
        """Return {"online": bool, "model": str, "model_installed": bool}."""
        now = time.monotonic()
        if not force and self._status and now - self._status_checked < self.STATUS_TTL:
            return self._status
        try:
            tags = self._request("/api/tags", timeout=2)
            names = {m.get("name", "") for m in tags.get("models", [])}
            # "llama3.2" matches "llama3.2:latest"
            installed = self.model in names or f"{self.model}:latest" in names
            self._status = {"online": True, "model": self.model, "model_installed": installed}
        except (urllib.error.URLError, OSError, ValueError):
            self._status = {"online": False, "model": self.model, "model_installed": False}
        self._status_checked = now
        return self._status

    def is_available(self):
        s = self.status()
        return s["online"] and s["model_installed"]

    def chat(self, messages, temperature=0.3):
        """Send a list of {"role", "content"} messages and return the reply text.

        Raises RuntimeError if the local model cannot be reached.
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature},
        }
        try:
            result = self._request("/api/chat", payload)
        except (urllib.error.URLError, OSError, ValueError) as exc:
            # Force a fresh status check next time
            self._status = None
            raise RuntimeError(f"Local model unavailable: {exc}") from exc
        content = (result.get("message") or {}).get("content", "").strip()
        if not content:
            raise RuntimeError("Local model returned an empty answer")
        return content
