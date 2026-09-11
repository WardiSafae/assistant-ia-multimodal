"""
Orchestrateur du protocole d'évaluation TTS.

Reproduit, à petite échelle, une démarche de certification IA typique en
contexte industriel exigeant (aéronautique, santé, finance) :
1. Prise en main de la solution TTS existante (ici : synthesize_speech)
2. Exécution d'une campagne de test sur des scénarios variés (test_sentences.json)
3. Mesure de l'intelligibilité via retranscription (Whisper) et calcul du WER
4. Verdict de conformité par catégorie et au global
5. Capitalisation des résultats dans un rapport Markdown

Usage :
    python -m src.evaluation.run_evaluation
"""

import json
import os
from datetime import datetime

TEST_SENTENCES_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "tts_evaluation", "test_sentences.json"
)
AUDIO_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "reports", "audio_samples")
RESULTS_JSON_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "reports", "evaluation_results.json")
REPORT_MD_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "reports", "evaluation_report.md")


def load_test_sentences(path: str = TEST_SENTENCES_PATH) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def evaluate_sentence(category: str, index: int, text: str) -> dict:
    """
    Synthétise une phrase, la retranscrit, calcule le WER et le verdict.
    """
    from src.evaluation.metrics import certification_verdict, word_error_rate
    from src.stt.transcribe import transcribe_audio
    from src.tts.synthesize import synthesize_speech

    audio_path = os.path.join(AUDIO_OUTPUT_DIR, f"{category}_{index}.mp3")
    synthesize_speech(text, output_path=audio_path)

    # transcribe_audio retourne un TranscriptionResult (dataclass)
    transcription = transcribe_audio(audio_path)

    wer = word_error_rate(reference=text, hypothesis=transcription.text)
    verdict = certification_verdict(wer)

    return {
        "category": category,
        "reference_text": text,
        "transcribed_text": transcription.text,
        "wer": round(wer, 4),
        "verdict": verdict,
        "audio_path": audio_path,
    }


def aggregate_by_category(results: list[dict]) -> dict:
    """
    Calcule le WER moyen et le taux de conformité par catégorie.
    Fonction pure, testable sans appel réseau (voir tests/).
    """
    categories = {}
    for result in results:
        cat = result["category"]
        categories.setdefault(cat, []).append(result)

    summary = {}
    for cat, items in categories.items():
        mean_wer = sum(r["wer"] for r in items) / len(items)
        conform_count = sum(1 for r in items if r["verdict"] == "Conforme")
        summary[cat] = {
            "nombre_de_tests": len(items),
            "wer_moyen": round(mean_wer, 4),
            "taux_de_conformite": round(conform_count / len(items), 4),
        }
    return summary


def _format_wer(wer: float) -> str:
    """Formate un WER en pourcentage, avec gestion de l'infini."""
    if wer == float("inf"):
        return "∞"
    return f"{wer:.1%}"

def build_markdown_report(results: list[dict], summary: dict) -> str:
    """Assemble le rapport Markdown final (méthodologie + résultats + recommandations)."""
    lines = [
        "# Rapport d'évaluation d'un système Text-to-Speech",
        "",
        f"*Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}*",
        "",
        "## 1. Méthodologie",
        "",
        "Chaque phrase de test est synthétisée par le système TTS, puis retranscrite "
        "par un système de reconnaissance vocale indépendant (Whisper). L'écart entre "
        "le texte d'origine et la transcription obtenue (Word Error Rate, WER) sert de "
        "proxy à l'intelligibilité de la synthèse : plus le WER est faible, plus la "
        "synthèse est jugée fidèle et compréhensible.",
        "",
        f"**Seuil de conformité retenu pour ce projet : WER ≤ 15%** "
        "(seuil indicatif, à ajuster selon le contexte réel d'usage — un système "
        "opérant en environnement réglementé exigerait une analyse de risque dédiée "
        "et probablement des seuils différenciés par catégorie de criticité).",
        "",
        "Les phrases de test sont réparties en catégories représentatives de "
        "difficultés connues en synthèse vocale : phrases courtes/longues, "
        "chiffres, sigles/acronymes, noms propres, homographes ambigus.",
        "",
        "## 2. Résultats par catégorie",
        "",
        "| Catégorie | Nb tests | WER moyen | Taux de conformité |",
        "|---|---|---|---|",
    ]

    for cat, stats in summary.items():
        lines.append(
            f"| {cat} | {stats['nombre_de_tests']} | "
            f"{_format_wer(stats['wer_moyen'])} | {stats['taux_de_conformite']:.0%} |"
        )

    lines += ["", "## 3. Détail des tests", ""]
    for result in results:
        lines += [
            f"### {result['category']} — verdict : {result['verdict']} (WER = {_format_wer(result['wer'])})",
            f"- **Texte de référence** : {result['reference_text']}",
            f"- **Texte retranscrit** : {result['transcribed_text']}",
            "",
        ]

    worst_category = max(summary.items(), key=lambda kv: kv[1]["wer_moyen"])
    lines += [
        "## 4. Recommandations",
        "",
        f"- La catégorie la plus problématique est **{worst_category[0]}** "
        f"(WER moyen de {worst_category[1]['wer_moyen']:.1%}) : c'est un axe "
        "d'amélioration prioritaire pour le système testé.",
        "- Ce protocole reste une preuve de concept : une méthodologie de "
        "certification réelle nécessiterait un jeu de test bien plus large, "
        "une évaluation humaine complémentaire (le WER seul ne capture pas la "
        "prosodie ni le naturel de la voix), et une analyse de robustesse face "
        "au bruit ou à des conditions dégradées.",
        "",
    ]

    return "\n".join(lines)


def run_evaluation() -> None:
    os.makedirs(AUDIO_OUTPUT_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(REPORT_MD_PATH), exist_ok=True)

    sentences_by_category = load_test_sentences()

    results = []
    for category, sentences in sentences_by_category.items():
        for index, text in enumerate(sentences):
            print(f"Évaluation [{category}] #{index} : {text[:50]}...")
            results.append(evaluate_sentence(category, index, text))

    summary = aggregate_by_category(results)

    with open(RESULTS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump({"results": results, "summary": summary}, f, ensure_ascii=False, indent=2)

    report = build_markdown_report(results, summary)
    with open(REPORT_MD_PATH, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\nRésultats bruts : {RESULTS_JSON_PATH}")
    print(f"Rapport final   : {REPORT_MD_PATH}")


if __name__ == "__main__":
    run_evaluation()
