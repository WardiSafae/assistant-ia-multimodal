"""
Construction de l'index vectoriel (FAISS) à partir des documents du corpus.

À exécuter une fois avant d'utiliser le backend RAG :
    python -m src.backends.vector_rag.build_index

Ce module démontre la construction d'une base vectorielle pour un système de
Retrieval-Augmented Generation (RAG) : indexation d'un corpus de documents,
recherche par similarité sémantique.
"""

import glob
import os
import pickle

CORPUS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "corpus")
INDEX_DIR = os.path.join(os.path.dirname(__file__), "index")
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
CHUNK_SIZE_WORDS = 120
CHUNK_OVERLAP_WORDS = 20


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE_WORDS, overlap: int = CHUNK_OVERLAP_WORDS) -> list[str]:
    """
    Découpe un texte en morceaux (chunks) de taille fixe, avec chevauchement,
    pour préserver le contexte entre deux morceaux consécutifs.
    """
    words = text.split()
    if len(words) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunks.append(" ".join(words[start:end]))
        start += chunk_size - overlap
    return chunks


def load_corpus(corpus_dir: str = CORPUS_DIR) -> list[dict]:
    """
    Charge tous les fichiers .md du dossier corpus et les découpe en chunks.
    Retourne une liste de dicts {"text": ..., "source": ...}.
    """
    documents = []
    for filepath in sorted(glob.glob(os.path.join(corpus_dir, "*.md"))):
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        source_name = os.path.basename(filepath)
        for chunk in chunk_text(content):
            documents.append({"text": chunk, "source": source_name})
    return documents


def build_index(corpus_dir: str = CORPUS_DIR, index_dir: str = INDEX_DIR) -> None:
    """
    Construit l'index FAISS et sauvegarde à la fois l'index et les métadonnées
    (texte + source de chaque chunk) sur disque.
    """
    # Imports différés : faiss et sentence-transformers sont des dépendances
    # lourdes, inutiles pour simplement découper du texte (voir tests/).
    import faiss
    from sentence_transformers import SentenceTransformer

    os.makedirs(index_dir, exist_ok=True)

    print(f"Chargement du corpus depuis {corpus_dir} ...")
    documents = load_corpus(corpus_dir)
    print(f"{len(documents)} chunks générés à partir du corpus.")

    print(f"Chargement du modèle d'embeddings ({EMBEDDING_MODEL_NAME}) ...")
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    texts = [doc["text"] for doc in documents]
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    faiss.write_index(index, os.path.join(index_dir, "corpus.faiss"))
    with open(os.path.join(index_dir, "metadata.pkl"), "wb") as f:
        pickle.dump(documents, f)

    print(f"Index sauvegardé dans {index_dir}/ ({len(documents)} chunks indexés).")


if __name__ == "__main__":
    build_index()
