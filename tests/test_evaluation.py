"""
Tests unitaires pour le module d'évaluation TTS — aucune dépendance réseau,
aucun appel à un modèle TTS ou STT réel.
"""

from ..src.evaluation.metrics import (
    certification_verdict,
    normalize_text,
    word_error_rate,
)
from ..src.evaluation.run_evaluation import aggregate_by_category


# ---- Tests de normalisation ----

def test_normalize_text_lowercases_and_strips_punctuation():
    assert normalize_text("Bonjour, comment allez-vous ?") == "bonjour comment allezvous"


def test_normalize_text_collapses_multiple_spaces():
    assert normalize_text("Un   texte    avec   espaces") == "un texte avec espaces"


# ---- Tests du Word Error Rate ----

def test_wer_identical_texts_is_zero():
    assert word_error_rate("Bonjour le monde", "Bonjour le monde") == 0.0


def test_wer_completely_different_texts_is_one():
    # 3 mots de référence, 3 substitutions nécessaires
    assert word_error_rate("chat chien oiseau", "table stylo lampe") == 1.0


def test_wer_partial_error():
    # "le chat noir" -> "le chat blanc" : 1 substitution sur 3 mots = WER 1/3
    wer = word_error_rate("le chat noir", "le chat blanc")
    assert abs(wer - (1 / 3)) < 1e-6


def test_wer_ignores_case_and_punctuation():
    assert word_error_rate("Bonjour, le monde !", "bonjour le monde") == 0.0


def test_wer_empty_reference_and_empty_hypothesis_is_zero():
    assert word_error_rate("", "") == 0.0


# ---- Tests du verdict de certification ----

def test_certification_verdict_conforme_below_threshold():
    assert certification_verdict(0.05, threshold=0.15) == "Conforme"


def test_certification_verdict_non_conforme_above_threshold():
    assert certification_verdict(0.30, threshold=0.15) == "Non conforme"


def test_certification_verdict_exactly_at_threshold_is_conforme():
    assert certification_verdict(0.15, threshold=0.15) == "Conforme"


# ---- Tests de l'agrégation par catégorie ----

def _sample_results():
    return [
        {"category": "phrases_courtes", "wer": 0.0, "verdict": "Conforme"},
        {"category": "phrases_courtes", "wer": 0.2, "verdict": "Non conforme"},
        {"category": "chiffres_et_nombres", "wer": 0.5, "verdict": "Non conforme"},
    ]


def test_aggregate_by_category_computes_mean_wer():
    summary = aggregate_by_category(_sample_results())
    assert summary["phrases_courtes"]["wer_moyen"] == 0.1
    assert summary["chiffres_et_nombres"]["wer_moyen"] == 0.5


def test_aggregate_by_category_computes_conformity_rate():
    summary = aggregate_by_category(_sample_results())
    assert summary["phrases_courtes"]["taux_de_conformite"] == 0.5
    assert summary["chiffres_et_nombres"]["taux_de_conformite"] == 0.0


if __name__ == "__main__":
    test_normalize_text_lowercases_and_strips_punctuation()
    test_normalize_text_collapses_multiple_spaces()
    test_wer_identical_texts_is_zero()
    test_wer_completely_different_texts_is_one()
    test_wer_partial_error()
    test_wer_ignores_case_and_punctuation()
    test_wer_empty_reference_and_empty_hypothesis_is_zero()
    test_certification_verdict_conforme_below_threshold()
    test_certification_verdict_non_conforme_above_threshold()
    test_certification_verdict_exactly_at_threshold_is_conforme()
    test_aggregate_by_category_computes_mean_wer()
    test_aggregate_by_category_computes_conformity_rate()
    print("Tous les tests sont passés ✓")
