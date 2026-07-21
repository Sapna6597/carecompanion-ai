"""MD AI Showcase — patient-facing health web app.

A Flask application demonstrating patient-oriented, AI-assisted health tools:
an educational symptom checker, a health assistant chat, and daily health tips.
The symptom checker uses a scikit-learn model with open-data enrichment. The chat
assistant uses OpenAI when an API key is configured, and falls back to an offline
rule-based assistant otherwise.

Run:
    python app.py
Then open http://127.0.0.1:5000 in your browser.
"""

from __future__ import annotations

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

load_dotenv()  # Load OPENAI_API_KEY and friends from a local .env file if present.

from ai import assistant, health_tips, llm_assistant, symptom_checker
from ai import knowledge_base

app = Flask(__name__)


@app.route("/")
def index():
    """Render the single-page app."""
    return render_template("index.html", tip=health_tips.tip_of_the_day())


@app.get("/api/symptoms")
def api_symptoms():
    """Return the symptom vocabulary the model understands."""
    return jsonify({"symptoms": knowledge_base.symptom_vocabulary()})


@app.post("/api/symptom-check")
def api_symptom_check():
    """Analyze a list of symptoms and return an educational assessment."""
    data = request.get_json(silent=True) or {}
    symptoms = data.get("symptoms", [])
    if not isinstance(symptoms, list):
        return jsonify({"error": "'symptoms' must be a list of strings."}), 400
    return jsonify(symptom_checker.check_symptoms(symptoms))


@app.post("/api/chat")
def api_chat():
    """Return an assistant reply, preferring the OpenAI LLM when available."""
    data = request.get_json(silent=True) or {}
    message = data.get("message", "")
    if not isinstance(message, str):
        return jsonify({"error": "'message' must be a string."}), 400

    result = llm_assistant.reply(message)
    if result is None:
        result = assistant.reply(message)
        result["source"] = "rule-based (offline)"
    return jsonify(result)


@app.get("/api/assistant-mode")
def api_assistant_mode():
    """Report whether the LLM assistant is active."""
    return jsonify({"llm": llm_assistant.is_available()})


@app.get("/api/health-tips")
def api_health_tips():
    """Return the full catalogue of health tips."""
    return jsonify(health_tips.all_tips())


@app.get("/api/health")
def api_health():
    """Simple health/liveness endpoint."""
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
