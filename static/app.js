// Shared helpers: text size, read-aloud and assistant status.
(function () {
    "use strict";

    function store(key, value) {
        try {
            if (value === undefined) return localStorage.getItem(key);
            localStorage.setItem(key, value);
        } catch (e) { /* storage may be blocked - the app still works */ }
        return null;
    }

    // Text size
    function setSize(size) {
        document.documentElement.dataset.textSize = size;
        document.querySelectorAll(".text-size button").forEach(function (b) {
            b.setAttribute("aria-pressed", String(b.dataset.size === size));
        });
        store("guardian-text-size", size);
    }
    setSize(store("guardian-text-size") || "large");
    document.querySelectorAll(".text-size button").forEach(function (b) {
        b.addEventListener("click", function () { setSize(b.dataset.size); });
    });

    // Read text aloud using the browser's built-in voice (works offline on most systems)
    function speak(text) {
        if (!("speechSynthesis" in window)) return;
        window.speechSynthesis.cancel();
        var utter = new SpeechSynthesisUtterance(text.replace(/[\u{1F300}-\u{1FAFF}☀-➿]/gu, ""));
        utter.rate = 0.9;
        window.speechSynthesis.speak(utter);
    }

    // Show whether the offline AI model is running
    function checkStatus() {
        var el = document.getElementById("ai-status");
        if (!el) return;
        fetch("/api/status").then(function (r) { return r.json(); }).then(function (s) {
            if (s.online && s.model_installed) {
                el.textContent = "🟢 Offline AI assistant ready (" + s.model + ")";
            } else if (s.online) {
                el.textContent = "🟡 AI model \"" + s.model + "\" not installed yet - using the built-in safety guide";
            } else {
                el.textContent = "🟡 Using the built-in safety guide (offline AI model not running)";
            }
        }).catch(function () { el.textContent = ""; });
    }
    checkStatus();

    window.Guardian = { speak: speak, store: store };
})();
