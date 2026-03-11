"""
SentimentAI - API Flask exposant l'analyse de sentiment.
"""

from flask import Flask, request, jsonify
from src.sentiment import analyze, batch_analyze, get_summary

app = Flask(__name__)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "version": "0.1.0"})


@app.route("/analyze", methods=["POST"])
def analyze_text():
    data = request.get_json()
    if not data or "text" not in data:
        return jsonify({"error": "Champ 'text' requis"}), 400
    result = analyze(data["text"])
    return jsonify(result)


@app.route("/batch", methods=["POST"])
def batch():
    data = request.get_json()
    if not data or "texts" not in data:
        return jsonify({"error": "Champ 'texts' requis"}), 400
    results = batch_analyze(data["texts"])
    summary = get_summary(results)
    return jsonify({"results": results, "summary": summary})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
