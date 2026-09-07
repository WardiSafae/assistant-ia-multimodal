"""
Tests unitaires pour la logique de découpage en chunks (pas de dépendance
réseau ni de modèle — s'exécute rapidement en CI).
"""

from src.backends.vector_rag.build_index import chunk_text


def test_chunk_text_short_text_returns_single_chunk():
    text = "Ceci est un texte court."
    chunks = chunk_text(text, chunk_size=120, overlap=20)
    assert len(chunks) == 1
    assert chunks[0] == text


def test_chunk_text_long_text_produces_multiple_chunks():
    text = " ".join(["mot"] * 300)
    chunks = chunk_text(text, chunk_size=120, overlap=20)
    assert len(chunks) > 1


def test_chunk_text_overlap_preserves_context():
    text = " ".join(str(i) for i in range(300))
    chunks = chunk_text(text, chunk_size=120, overlap=20)
    first_chunk_words = chunks[0].split()
    second_chunk_words = chunks[1].split()
    # Les 20 derniers mots du premier chunk doivent apparaître au début du second
    assert first_chunk_words[-20:] == second_chunk_words[:20]


if __name__ == "__main__":
    test_chunk_text_short_text_returns_single_chunk()
    test_chunk_text_long_text_produces_multiple_chunks()
    test_chunk_text_overlap_preserves_context()
    print("Tous les tests sont passés ✓")
