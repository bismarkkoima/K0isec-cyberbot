// "Check a message" page.
(function () {
    "use strict";
    var form = document.getElementById("check-form");
    var input = document.getElementById("check-input");
    var result = document.getElementById("check-result");
    var LABELS = { high: "🔴 High risk", medium: "🟠 Some warning signs", low: "🟢 Low risk" };

    function el(tag, cls, text) {
        var e = document.createElement(tag);
        if (cls) e.className = cls;
        if (text) e.textContent = text;
        return e;
    }

    form.addEventListener("submit", function (e) {
        e.preventDefault();
        fetch("/api/check", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: input.value })
        }).then(function (r) { return r.json(); }).then(function (data) {
            if (data.error) { alert(data.error); return; }
            result.className = "card result risk-" + data.level;
            document.getElementById("result-headline").textContent = LABELS[data.level] + ": " + data.headline;

            var flags = document.getElementById("result-flags");
            flags.replaceChildren();
            if (data.flags.length) {
                flags.appendChild(el("h3", null, "Warning signs I found"));
                var list = el("ul", "flag-list");
                data.flags.forEach(function (f) {
                    var li = el("li");
                    li.appendChild(el("strong", null, f.title));
                    li.appendChild(el("span", null, " - " + f.explanation));
                    list.appendChild(li);
                });
                flags.appendChild(list);
            }

            var advice = document.getElementById("result-advice");
            advice.replaceChildren();
            data.advice.forEach(function (a) { advice.appendChild(el("li", null, a)); });

            result.hidden = false;
            result.scrollIntoView({ behavior: "smooth" });
        }).catch(function () { alert("Sorry, the check could not be completed. Please try again."); });
    });
})();
