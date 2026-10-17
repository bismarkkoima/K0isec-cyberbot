"""K0isec Guardian - an offline cyber-safety assistant for older adults.

Run with:  python app.py   then open http://127.0.0.1:5000
"""

import os

from dotenv import load_dotenv
from flask import Flask, abort, jsonify, render_template, request

from guardian import knowledge, lessons, scam_checker
from guardian.assistant import Assistant

load_dotenv()


def create_app(assistant=None):
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 64 * 1024  # reject very large requests
    bot = assistant or Assistant()

    @app.after_request
    def security_headers(resp):
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["X-Frame-Options"] = "DENY"
        resp.headers["Referrer-Policy"] = "no-referrer"
        resp.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:"
        )
        return resp

    # ---- Pages ----------------------------------------------------------

    @app.route("/")
    def index():
        return render_template("index.html", topics=knowledge.TOPICS)

    @app.route("/check")
    def check_page():
        return render_template("check.html")

    @app.route("/lessons")
    def lessons_page():
        return render_template("lessons.html", lessons=lessons.LESSONS)

    @app.route("/lessons/<lesson_id>")
    def lesson_page(lesson_id):
        lesson = lessons.get_lesson(lesson_id)
        if lesson is None:
            abort(404)
        return render_template("lesson.html", lesson=lesson)

    @app.route("/help")
    def help_page():
        return render_template("help.html", topic=knowledge.get_topic("been-scammed"))

    # ---- JSON API -------------------------------------------------------

    def _json():
        data = request.get_json(silent=True)
        return data if isinstance(data, dict) else {}

    @app.route("/api/chat", methods=["POST"])
    def api_chat():
        data = _json()
        message = data.get("message")
        if not isinstance(message, str) or not message.strip():
            return jsonify({"error": "Please type a message."}), 400
        history = data.get("history")
        if not isinstance(history, list):
            history = []
        history = [h for h in history if isinstance(h, dict)]
        return jsonify(bot.reply(message, history))

    @app.route("/api/check", methods=["POST"])
    def api_check():
        text = _json().get("text")
        if not isinstance(text, str) or not text.strip():
            return jsonify({"error": "Please paste the message you want to check."}), 400
        return jsonify(scam_checker.analyze(text))

    @app.route("/api/topic/<topic_id>")
    def api_topic(topic_id):
        topic = knowledge.get_topic(topic_id)
        if topic is None:
            return jsonify({"error": "Topic not found"}), 404
        return jsonify({"reply": f"{topic['icon']} {topic['title']}\n\n{topic['answer']}",
                        "source": "safety-guide"})

    @app.route("/api/status")
    def api_status():
        return jsonify(bot.llm.status())

    @app.errorhandler(404)
    def not_found(_):
        return render_template("404.html"), 404

    return app


app = create_app()

if __name__ == "__main__":
    # Bind to this computer only; nothing is exposed to the network.
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5000")),
            debug=os.getenv("FLASK_DEBUG") == "1")
