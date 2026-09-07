# Assistant IA multimodal — Speech-to-Text + RAG + LLM

Projet personnel démontrant un pipeline modulaire : une question posée à l'oral ou à l'écrit
est transcrite (Speech-to-Text), enrichie par une base de connaissances (RAG vectoriel ou
graphe de connaissances), puis répondue par un LLM.

## Pourquoi ce projet

Ce projet a été conçu pour être **modulaire par backend** : le même pipeline
(transcription → récupération de contexte → génération de réponse) peut s'appuyer sur
deux sources de connaissances interchangeables, sans changer le reste du code.

C'est un projet d'auto-formation en lien avec mon parcours (Master BDSI — NLP, Speech-to-Text,
IA distribuée), construit pour appuyer mes candidatures de stage de fin d'études.

## Architecture

```
Question (voix ou texte)
        │
        ▼
Transcription (STT — Whisper)
        │
        ▼
   ┌────┴────┐
   ▼         ▼
Backend    Backend
vectoriel  graphe de
(RAG)      connaissances
   │         │
   └────┬────┘
        ▼
Génération de réponse (LLM)
        │
        ▼
   Réponse (texte)
   [+ voix via TTS — étape 3]
```

Le module `backends/` expose une interface commune (`query(question) -> contexte`) :
n'importe quel backend qui la respecte peut être branché sans toucher au reste du pipeline.

## Statut d'avancement

- [x] **Étape 1 — STT + Backend vectoriel (RAG) + LLM** ← ce commit
- [ ] Étape 2 — Backend graphe de connaissances (NetworkX/Neo4j)
- [ ] Étape 3 — Synthèse vocale (TTS) + module d'évaluation

## Installation

```bash
python -m venv venv
source venv/bin/activate  # Windows : venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # puis renseigner votre clé API LLM dans .env
```

## Utilisation

1. Indexer le corpus de documents (dossier `data/corpus/`) :
   ```bash
   python -m src.backends.vector_rag.build_index
   ```

2. Poser une question (texte ou fichier audio) :
   ```bash
   python -m src.main --text "Qu'est-ce que le projet PM2.5 ?"
   python -m src.main --audio chemin/vers/question.wav
   ```

## Corpus de démonstration

Le dossier `data/corpus/` contient des résumés de mes propres projets académiques
(PM2.5/Federated Learning, EventGuard/Cloud, ASR/PFE) — l'assistant peut ainsi répondre
à des questions sur mon propre parcours, ce qui sert aussi de démo en entretien.
Vous pouvez remplacer ces fichiers par votre propre corpus.

## Choix techniques

| Brique | Outil | Pourquoi |
|---|---|---|
| Transcription | [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | Open source, léger, tourne en local |
| Embeddings | `sentence-transformers` (all-MiniLM-L6-v2) | Gratuit, local, pas de clé API nécessaire |
| Base vectorielle | FAISS | Standard, rapide, local |
| Orchestration LLM | LangChain | Cité explicitement dans plusieurs offres de stage ciblées |
| LLM de génération | Configurable (Mistral API, OpenAI-compatible, ou Ollama local) | Flexibilité selon budget/API disponible |

## Comment ce projet s'adapte à mes candidatures

- **Stage NLP/GenAI (ex. Sia)** → l'accent est mis sur le backend RAG et l'usage de LangChain.
- **Stage recherche appliquée (ex. Astek)** → l'étape 2 (graphe de connaissances) devient la
  démonstration principale, avec un requêtage en langage naturel sur le graphe.
- **Stage Data Science / certification IA (ex. OCTO)** → l'étape 3 (TTS + évaluation) devient
  la démonstration principale : protocole de test sur la sortie vocale générée.

## Licence

Projet personnel à but pédagogique et de candidature. Libre de réutilisation.
