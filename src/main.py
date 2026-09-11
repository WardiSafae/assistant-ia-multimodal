"""
Point d'entrée principal du pipeline : question (texte ou audio) -> contexte
récupéré -> réponse générée par le LLM.

Le backend de récupération de contexte est choisi via --backend :
    rag   : recherche vectorielle (Retrieval-Augmented Generation)
    graph : graphe de connaissances (entités et relations)
Les deux respectent la même interface query(question) -> contexte, ce qui
permet de les échanger sans toucher au reste du pipeline.

Usage :
    python -m src.main --text "Qu'est-ce que le projet PM2.5 ?"
    python -m src.main --text "..." --backend graph
    python -m src.main --audio chemin/vers/question.wav
"""

import argparse

from src.generation.generate_answer import generate_answer
from src.stt.transcribe import transcribe_audio


def get_question_text(args: argparse.Namespace) -> str:
    """Renvoie la question sous forme de texte, en transcrivant l'audio si besoin."""
    if args.audio:
        print(f"Transcription de {args.audio} ...")
        result = transcribe_audio(args.audio)
        print(f"Question transcrite : {result.text}")
        return result.text
    return args.text


def get_backend(name: str):
    """Instancie le backend demandé (rag ou graph)."""
    if name == "graph":
        from src.backends.knowledge_graph.graph_query import KnowledgeGraphBackend

        return KnowledgeGraphBackend()

    from src.backends.vector_rag.retriever import VectorRAGBackend

    return VectorRAGBackend()


def main() -> None:
    parser = argparse.ArgumentParser(description="Assistant IA multimodal (STT + backend modulaire + LLM)")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--text", type=str, help="Question posée directement en texte")
    group.add_argument("--audio", type=str, help="Chemin vers un fichier audio contenant la question")
    parser.add_argument(
        "--backend",
        choices=["rag", "graph"],
        default="rag",
        help="Backend de récupération de contexte à utiliser (défaut : rag)",
    )
    args = parser.parse_args()

    question = get_question_text(args)

    print(f"\nRecherche du contexte pertinent (backend : {args.backend}) ...")
    backend = get_backend(args.backend)
    context = backend.query(question)

    if not context:
        print("Aucun contexte pertinent trouvé dans la base de connaissances.")

    print("\nGénération de la réponse ...")
    answer = generate_answer(question, context)

    print("\n" + "=" * 60)
    print(f"Question : {question}")
    print("-" * 60)
    print(f"Réponse : {answer}")
    print("=" * 60)


if __name__ == "__main__":
    main()
