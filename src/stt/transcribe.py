"""
Module de transcription audio (Speech-to-Text) basé sur faster-whisper.

Ce module est la brique commune aux trois angles de candidature :
- Sia / Astek : transcrit la question orale de l'utilisateur avant de la router
  vers le backend choisi (RAG ou graphe de connaissances).
- OCTO : réutilisé "à l'envers" dans le module d'évaluation (étape 3) pour
  retranscrire un audio généré par un système TTS et mesurer son intelligibilité.
"""

import os
from dataclasses import dataclass
from functools import lru_cache

from faster_whisper import WhisperModel


@dataclass
class TranscriptionResult:
    text: str
    language: str
    duration_seconds: float


@lru_cache(maxsize=1)
def _load_model(model_size: str = None) -> WhisperModel:
    """
    Charge le modèle Whisper une seule fois (mis en cache) pour éviter de le
    recharger à chaque appel. La taille du modèle est configurable via la
    variable d'environnement WHISPER_MODEL_SIZE (voir .env.example).
    """
    size = model_size or os.getenv("WHISPER_MODEL_SIZE", "base")
    # compute_type="int8" permet de tourner correctement sur CPU sans GPU dédié
    return WhisperModel(size, device="cpu", compute_type="int8")


def transcribe_audio(audio_path: str, model_size: str = None) -> TranscriptionResult:
    """
    Transcrit un fichier audio (wav, mp3, m4a, ...) en texte.

    Args:
        audio_path: chemin vers le fichier audio à transcrire.
        model_size: taille du modèle Whisper (tiny/base/small/medium/large-v3).
                    Si None, utilise WHISPER_MODEL_SIZE depuis l'environnement.

    Returns:
        TranscriptionResult contenant le texte transcrit, la langue détectée
        et la durée de l'audio.
    """
    model = _load_model(model_size)
    segments, info = model.transcribe(audio_path, beam_size=5)

    full_text = " ".join(segment.text.strip() for segment in segments)

    return TranscriptionResult(
        text=full_text.strip(),
        language=info.language,
        duration_seconds=info.duration,
    )


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage : python -m src.stt.transcribe <chemin_audio>")
        sys.exit(1)

    result = transcribe_audio(sys.argv[1])
    print(f"Langue détectée : {result.language}")
    print(f"Durée : {result.duration_seconds:.1f}s")
    print(f"Transcription : {result.text}")
