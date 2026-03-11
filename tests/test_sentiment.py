"""Tests pour le module sentiment.py - coverage cible >= 70%"""

import pytest
from src.sentiment import analyze, preprocess, batch_analyze, get_summary


# ─── preprocess ───────────────────────────────────────────────────────────────

class TestPreprocess:
    def test_lowercase(self):
        assert preprocess("Bonjour") == ["bonjour"]

    def test_removes_punctuation(self):
        result = preprocess("Bien! Super.")
        assert "bien" in result
        assert "super" in result

    def test_empty_string(self):
        assert preprocess("") == []

    def test_multiple_spaces(self):
        assert preprocess("  bon   bien  ") == ["bon", "bien"]

    def test_raises_on_non_string(self):
        with pytest.raises(TypeError):
            preprocess(123)

    def test_raises_on_none(self):
        with pytest.raises(TypeError):
            preprocess(None)


# ─── analyze ──────────────────────────────────────────────────────────────────

class TestAnalyze:
    def test_positive_text(self):
        result = analyze("C'est super et excellent")
        assert result["label"] == "positive"
        assert result["score"] > 0
        assert result["positive_count"] >= 2

    def test_negative_text(self):
        result = analyze("C'est horrible et terrible")
        assert result["label"] == "negative"
        assert result["score"] < 0
        assert result["negative_count"] >= 2

    def test_neutral_text(self):
        result = analyze("Il fait beau aujourd'hui")
        assert result["label"] == "neutral"
        assert result["score"] == 0.0

    def test_empty_text(self):
        result = analyze("")
        assert result["label"] == "neutral"
        assert result["score"] == 0.0
        assert result["positive_count"] == 0
        assert result["negative_count"] == 0

    def test_mixed_text(self):
        result = analyze("super horrible")
        assert result["label"] == "neutral"
        assert result["score"] == 0.0

    def test_result_keys(self):
        result = analyze("bien")
        assert set(result.keys()) == {"label", "score", "positive_count", "negative_count"}

    def test_score_range(self):
        result = analyze("super bien excellent")
        assert -1.0 <= result["score"] <= 1.0

    def test_english_positive(self):
        result = analyze("This is great and amazing")
        assert result["label"] == "positive"

    def test_english_negative(self):
        result = analyze("This is awful and horrible bad")
        assert result["label"] == "negative"

    def test_only_punctuation(self):
        result = analyze("!!! ??? ...")
        assert result["label"] == "neutral"


# ─── batch_analyze ────────────────────────────────────────────────────────────

class TestBatchAnalyze:
    def test_basic_batch(self):
        texts = ["super", "horrible", "neutre"]
        results = batch_analyze(texts)
        assert len(results) == 3

    def test_labels_in_batch(self):
        texts = ["super bien", "mauvais horrible", "bonjour"]
        results = batch_analyze(texts)
        assert results[0]["label"] == "positive"
        assert results[1]["label"] == "negative"
        assert results[2]["label"] == "neutral"

    def test_empty_list(self):
        assert batch_analyze([]) == []

    def test_raises_on_non_list(self):
        with pytest.raises(TypeError):
            batch_analyze("texte")

    def test_single_element(self):
        results = batch_analyze(["excellent"])
        assert len(results) == 1
        assert results[0]["label"] == "positive"


# ─── get_summary ──────────────────────────────────────────────────────────────

class TestGetSummary:
    def test_empty_results(self):
        summary = get_summary([])
        assert summary["total"] == 0
        assert summary["average_score"] == 0.0

    def test_counts(self):
        results = [
            {"label": "positive", "score": 1.0, "positive_count": 1, "negative_count": 0},
            {"label": "negative", "score": -1.0, "positive_count": 0, "negative_count": 1},
            {"label": "neutral", "score": 0.0, "positive_count": 0, "negative_count": 0},
        ]
        summary = get_summary(results)
        assert summary["total"] == 3
        assert summary["positive"] == 1
        assert summary["negative"] == 1
        assert summary["neutral"] == 1

    def test_average_score(self):
        results = [
            {"label": "positive", "score": 1.0, "positive_count": 1, "negative_count": 0},
            {"label": "negative", "score": -1.0, "positive_count": 0, "negative_count": 1},
        ]
        summary = get_summary(results)
        assert summary["average_score"] == 0.0

    def test_all_positive(self):
        results = batch_analyze(["super", "excellent", "génial"])
        summary = get_summary(results)
        assert summary["positive"] == 3
        assert summary["negative"] == 0

    def test_summary_keys(self):
        summary = get_summary([{"label": "neutral", "score": 0.0,
                                "positive_count": 0, "negative_count": 0}])
        assert set(summary.keys()) == {"total", "positive", "negative", "neutral", "average_score"}
