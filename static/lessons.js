// Lesson list (completed badges) and lesson quiz.
(function () {
    "use strict";
    var done = {};
    try { done = JSON.parse(Guardian.store("guardian-lessons-done") || "{}"); } catch (e) { done = {}; }

    document.querySelectorAll("[data-lesson-done]").forEach(function (el) {
        if (done[el.dataset.lessonDone]) el.hidden = false;
    });

    var readBtn = document.getElementById("read-lesson");
    if (readBtn) {
        readBtn.addEventListener("click", function () {
            var text = Array.prototype.map.call(document.querySelectorAll(".lesson-points li"),
                function (li) { return li.textContent; }).join(". ");
            Guardian.speak(text);
        });
    }

    var quiz = document.getElementById("quiz");
    if (!quiz) return;
    var questions = quiz.querySelectorAll(".quiz-question");
    var answered = 0, correct = 0;

    questions.forEach(function (q) {
        var right = Number(q.dataset.answer);
        var feedback = q.querySelector(".quiz-feedback");
        var options = q.querySelectorAll(".quiz-option");
        options.forEach(function (opt) {
            opt.addEventListener("click", function () {
                if (q.dataset.done) return;
                q.dataset.done = "1";
                var ok = Number(opt.dataset.index) === right;
                options.forEach(function (o) {
                    o.disabled = true;
                    if (Number(o.dataset.index) === right) o.classList.add("correct");
                });
                if (!ok) opt.classList.add("wrong");
                feedback.textContent = (ok ? "✅ Well done! " : "❌ Not quite. ") + feedback.dataset.why;
                feedback.hidden = false;
                answered += 1;
                if (ok) correct += 1;
                if (answered === questions.length) finish();
            });
        });
    });

    function finish() {
        var score = document.getElementById("quiz-score");
        score.textContent = "You got " + correct + " out of " + questions.length + " right. " +
            (correct === questions.length ? "Excellent - you're a scam spotter!" : "Good effort - every lesson makes you safer.");
        score.hidden = false;
        done[quiz.dataset.lessonId] = true;
        Guardian.store("guardian-lessons-done", JSON.stringify(done));
    }
})();
