"""
Module de synthèse vocale (Text-to-Speech).

Ce module joue le rôle d'une "solution TTS existante" que l'on cherche à
évaluer et fiabiliser (voir src/evaluation/). Le moteur est choisi
volontairement simple (gTTS) pour se concentrer sur la méthodologie
d'évaluation plutôt que sur la sophistication du modèle — l'interface est
cependant conçue pour qu'un moteur plus avancé (Coqui TTS, Piper,
ElevenLabs, ...) puisse être branché à la place sans changer le reste du
pipeline.
"""

import os
from dataclasses import dataclass


@dataclass
class SynthesisResult:
    audio_path: str
    text: str
    engine: str


def synthesize_speech(text: str, output_path: str, lang: str = "fr", engine: str = None) -> SynthesisResult:
    """
    Synthétise un texte en fichier audio.

    Args:
        text: texte à synthétiser.
        output_path: chemin de sortie du fichier audio (.mp3).
        lang: code langue (fr, en, ...).
        engine: moteur TTS à utiliser. Actuellement seul "gtts" est implémenté ;
                le paramètre existe pour permettre d'ajouter d'autres moteurs
                (Coqui TTS, Piper, ...) sans changer la signature de la fonction.

    Returns:
        SynthesisResult avec le chemin du fichier généré.
    """
    engine = engine or os.getenv("TTS_ENGINE", "gtts")

    if engine == "gtts":
        from gtts import gTTS

        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        tts = gTTS(text=text, lang=lang)
        tts.save(output_path)
        return SynthesisResult(audio_path=output_path, text=text, engine="gtts")

    raise NotImplementedError(
        f"Moteur TTS '{engine}' non implémenté. "
        "Seul 'gtts' est disponible actuellement — voir le docstring du module "
        "pour brancher un autre moteur (Coqui TTS, Piper, ...)."
    )


if __name__ == "__main__":
    result = synthesize_speech(
        "Ceci est un test de synthèse vocale.",
        output_path="reports/audio_samples/demo.mp3",
    )
    print(f"Audio généré : {result.audio_path} (moteur : {result.engine})")
