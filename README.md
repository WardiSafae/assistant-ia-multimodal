# Assistant IA multimodal — STT, RAG, Graphe de connaissances, TTS

Pipeline modulaire de bout en bout autour de la parole et du langage : une
question posée à l'oral ou à l'écrit est transcrite (Speech-to-Text), enrichie
par une base de connaissances interchangeable (recherche vectorielle **ou**
graphe de connaissances), répondue par un LLM, et peut être restituée à
l'oral (Text-to-Speech) — dont la fiabilité est elle-même mesurée par un
module d'évaluation dédié.

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
   Réponse texte
        │
        ▼ (optionnel)
Synthèse vocale (TTS) ──► Réponse orale
        │
        ▼
Module d'évaluation : retranscription (STT) de la réponse orale et
calcul du taux d'erreur (WER) pour mesurer sa fiabilité
```

Le module `backends/` expose une interface commune (`query(question) -> contexte`) :
n'importe quel backend qui la respecte peut être branché sans toucher au reste du pipeline.

## Statut d'avancement

- [x] Étape 1 — STT + Backend vectoriel (RAG) + LLM
- [x] Étape 2 — Backend graphe de connaissances (NetworkX + extraction LLM)
- [x] Étape 3 — Synthèse vocale (TTS) + module d'évaluation

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
   # Backend RAG (recherche vectorielle)
   python -m src.backends.vector_rag.build_index

   # Backend graphe de connaissances (entités et relations)
   python -m src.backends.knowledge_graph.build_graph
   ```

2. Poser une question (texte ou fichier audio) :
   ```bash
   python -m src.main --text "Qu'est-ce que le projet PM2.5 ?"                    # backend RAG (défaut)
   python -m src.main --text "Qu'est-ce que le projet PM2.5 ?" --backend graph    # backend graphe
   python -m src.main --audio chemin/vers/question.wav
   ```

3. Lancer le protocole d'évaluation du système de synthèse vocale :
   ```bash
   python -m src.evaluation.run_evaluation
   ```
   Génère `reports/evaluation_report.md` (rapport lisible : méthodologie, résultats
   par catégorie, recommandations) et `reports/evaluation_results.json` (données brutes).

   Pensez à committer ce rapport une fois généré (`git add reports/evaluation_report.md`) :
   c'est un livrable concret, pas seulement du code.

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
| Graphe de connaissances | NetworkX + extraction de triplets par LLM | Léger, pas d'infrastructure serveur nécessaire (alternative : Neo4j) |
| Synthèse vocale | gTTS | Simple et fiable ; le projet porte sur la méthodologie d'évaluation, pas sur la sophistication du moteur TTS (une interface permet d'en brancher un autre, ex. Coqui TTS). **Nécessite une connexion internet** (contrairement au reste du pipeline, qui tourne en local). |
| Évaluation TTS | Word Error Rate (implémentation maison, distance de Levenshtein) via retranscription Whisper | Métrique standard du domaine, aucune dépendance supplémentaire lourde |
| Orchestration LLM | LangChain | Standard de facto pour l'orchestration RAG/agents, large écosystème et documentation |
| LLM de génération | ChatMistralAI (API Mistral, quota gratuit) ou Ollama en local | Flexibilité selon budget/API disponible |

## Ce que ce projet démontre

- **Modularité et conception logicielle** : un backend interchangeable
  (RAG vs graphe de connaissances) derrière une interface commune, sans
  duplication de logique.
- **Compréhension de bout en bout de la parole et du langage** : de la
  transcription (STT) à la génération de réponse (LLM), en passant par la
  synthèse (TTS) et sa propre évaluation.
- **Rigueur méthodologique** : le module d'évaluation ne se contente pas de
  "faire fonctionner" un système TTS, il **mesure** sa fiabilité selon des
  scénarios explicites, avec un seuil de conformité assumé et documenté.
- **IA distribuée et confidentialité** : dans le prolongement de mon projet
  d'apprentissage fédéré (voir `data/corpus/pm25_federated_learning.md`),
  ce projet illustre une même sensibilité à ne pas centraliser inutilement
  les données traitées.

## Licence

Projet personnel à but pédagogique et de candidature. Libre de réutilisation.
