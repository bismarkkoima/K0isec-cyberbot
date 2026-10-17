// Chat page: send questions, show answers, topic buttons, voice input.
(function () {
    "use strict";
    var form = document.getElementById("chat-form");
    var input = document.getElementById("user-input");
    var log = document.getElementById("chat-log");
    var readAloud = document.getElementById("read-aloud");
    var voiceBtn = document.getElementById("voice-btn");
    var history = [];
    var busy = false;

    readAloud.checked = Guardian.store("guardian-read-aloud") === "1";
    readAloud.addEventListener("change", function () {
        Guardian.store("guardian-read-aloud", readAloud.checked ? "1" : "0");
        if (!readAloud.checked && "speechSynthesis" in window) window.speechSynthesis.cancel();
    });

    function addMessage(text, role, source) {
        var el = document.createElement("div");
        el.className = "message " + role;
        text.split(/\n{2,}/).forEach(function (para) {
            var p = document.createElement("p");
            p.textContent = para;
            el.appendChild(p);
        });
        if (source) {
            var tag = document.createElement("p");
            tag.className = "source";
            tag.textContent = source === "offline-llm" ? "Answered by the offline AI" : "From the built-in safety guide";
            el.appendChild(tag);
        }
        if (role === "bot") {
            var btn = document.createElement("button");
            btn.type = "button";
            btn.className = "btn-link";
            btn.textContent = "🔊 Read aloud";
            btn.addEventListener("click", function () { Guardian.speak(text); });
            el.appendChild(btn);
        }
        log.appendChild(el);
        el.scrollIntoView({ behavior: "smooth", block: "start" });
        return el;
    }

    function showReply(data) {
        addMessage(data.reply, "bot", data.source);
        if (readAloud.checked) Guardian.speak(data.reply);
    }

    function request(url, options) {
        busy = true;
        var thinking = addMessage("Thinking…", "bot thinking");
        return fetch(url, options).then(function (r) { return r.json(); }).then(function (data) {
            thinking.remove();
            if (data.error) throw new Error(data.error);
            showReply(data);
            return data;
        }).catch(function (err) {
            thinking.remove();
            addMessage("Sorry, something went wrong: " + err.message + " Please try again.", "bot");
        }).finally(function () { busy = false; });
    }

    form.addEventListener("submit", function (e) {
        e.preventDefault();
        var message = input.value.trim();
        if (!message || busy) return;
        addMessage(message, "user");
        input.value = "";
        request("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: message, history: history })
        }).then(function (data) {
            if (!data) return;
            history.push({ role: "user", content: message }, { role: "assistant", content: data.reply });
            history = history.slice(-8);
        });
    });

    // Enter sends, Shift+Enter adds a new line
    input.addEventListener("keydown", function (e) {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            form.requestSubmit();
        }
    });

    document.querySelectorAll(".topic-btn").forEach(function (btn) {
        btn.addEventListener("click", function () {
            if (busy) return;
            addMessage(btn.textContent.trim(), "user");
            request("/api/topic/" + encodeURIComponent(btn.dataset.topic));
            form.scrollIntoView({ behavior: "smooth" });
        });
    });

    // Optional voice input where the browser supports it
    var Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (Recognition) {
        voiceBtn.hidden = false;
        voiceBtn.addEventListener("click", function () {
            var rec = new Recognition();
            rec.lang = document.documentElement.lang || "en";
            voiceBtn.textContent = "🎤 Listening…";
            rec.onresult = function (ev) { input.value = ev.results[0][0].transcript; input.focus(); };
            rec.onend = function () { voiceBtn.textContent = "🎤 Speak"; };
            rec.start();
        });
    }
})();
