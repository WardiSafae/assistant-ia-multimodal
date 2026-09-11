"""
Métriques d'évaluation de l'intelligibilité d'une synthèse vocale.

Principe : on synthétise un texte connu, on le retranscrit (Speech-to-Text),
puis on compare le texte original au texte retranscrit. Plus l'écart est
faible, plus la synthèse est jugée intelligible.

Le Word Error Rate (WER) est la métrique standard du domaine : il compte le
nombre minimal de substitutions, insertions et suppressions de mots
nécessaires pour transformer la transcription en la référence, divisé par le
nombre de mots de la référence.

Toutes les fonctions de ce module sont pures (aucun appel réseau ni modèle) :
entièrement testables en isolation (voir tests/).
"""

import re
import string


def normalize_text(text: str) -> str:
    """
    Normalise un texte avant comparaison : minuscules, ponctuation retirée,
    espaces multiples réduits. Nécessaire car le TTS/STT ne préserve pas
    forcément la ponctuation ou la casse exacte du texte source.
    """
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"\s+", " ", text).strip()
    return text


def word_error_rate(reference: str, hypothesis: str) -> float:
    """
    Calcule le Word Error Rate entre un texte de référence et une hypothèse
    (transcription), via la distance d'édition au niveau mot (algorithme de
    Levenshtein, programmation dynamique).

    Retourne un flottant >= 0 (0 = transcription parfaite ; peut dépasser 1
    si la transcription contient beaucoup plus de mots que la référence).
    """
    ref_words = normalize_text(reference).split()
    hyp_words = normalize_text(hypothesis).split()

    if len(ref_words) == 0:
        return 0.0 if len(hyp_words) == 0 else float("inf")

    n, m = len(ref_words), len(hyp_words)
    dp = [[0] * (m + 1) for _ in range(n + 1)]

    for i in range(n + 1):
        dp[i][0] = i
    for j in range(m + 1):
        dp[0][j] = j

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if ref_words[i - 1] == hyp_words[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(
                    dp[i - 1][j],      # suppression
                    dp[i][j - 1],      # insertion
                    dp[i - 1][j - 1],  # substitution
                )

    edit_distance = dp[n][m]
    return edit_distance / n


# Seuil proposé pour ce projet : en dessous de 15% d'erreur sur les mots, la
# synthèse est jugée acceptable pour un usage informatif standard. Ce seuil
# devrait être ajusté selon le contexte réel d'usage (une méthodologie de
# certification aéronautique exigerait probablement un seuil plus strict et
# des catégories de sévérité différenciées).
DEFAULT_WER_THRESHOLD = 0.15


def certification_verdict(wer: float, threshold: float = DEFAULT_WER_THRESHOLD) -> str:
    """Rend un verdict simple à partir d'un WER et d'un seuil."""
    return "Conforme" if wer <= threshold else "Non conforme"
