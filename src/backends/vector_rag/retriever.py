"""
Backend de récupération vectorielle (RAG).

Expose l'interface commune attendue par le pipeline principal :
    query(question: str) -> str   (contexte pertinent pour répondre à la question)

C'est le cœur d'un système RAG classique : recherche par similarité
vectorielle, puis assemblage des passages les plus pertinents en contexte
pour le LLM de génération.
"""

import os
import pickle

from .build_index import EMBEDDING_MODEL_NAME, INDEX_DIR


class VectorRAGBackend:
    """Backend RAG : recherche par similarité vectorielle dans le corpus indexé."""

    def __init__(self, index_dir: str = INDEX_DIR, top_k: int = 3):
        import faiss
        from sentence_transformers import SentenceTransformer

        index_path = os.path.join(index_dir, "corpus.faiss")
        metadata_path = os.path.join(index_dir, "metadata.pkl")

        if not os.path.exists(index_path):
            raise FileNotFoundError(
                "Index introuvable. Lancez d'abord : "
                "python -m src.backends.vector_rag.build_index"
            )

        self.index = faiss.read_index(index_path)
        with open(metadata_path, "rb") as f:
            self.documents = pickle.load(f)

        self.model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        self.top_k = top_k

    def query(self, question: str) -> str:
        """
        Recherche les chunks les plus pertinents pour la question posée,
        et les assemble en un contexte unique destiné au LLM de génération.
        """
        question_embedding = self.model.encode([question], convert_to_numpy=True)
        distances, indices = self.index.search(question_embedding, self.top_k)

        retrieved_chunks = []
        for idx in indices[0]:
            if idx == -1:
                continue
            doc = self.documents[idx]
            retrieved_chunks.append(f"[Source : {doc['source']}]\n{doc['text']}")

        return "\n\n---\n\n".join(retrieved_chunks)


if __name__ == "__main__":
    backend = VectorRAGBackend()
    context = backend.query("Qu'est-ce que le projet PM2.5 ?")
    print(context)
