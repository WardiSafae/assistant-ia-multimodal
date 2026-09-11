"""
Tests unitaires pour le backend graphe de connaissances — aucune dépendance
réseau ni appel LLM : on teste uniquement le parsing et la logique de graphe.
"""

from ..src.backends.knowledge_graph.build_graph import (
    build_graph_from_triples,
    parse_triples_response,
)
from ..src.backends.knowledge_graph.graph_query import (
    find_matching_nodes,
    format_triples_as_context,
    parse_entities_response,
)


# ---- Tests de parsing (extraction de triplets) ----

def test_parse_triples_response_plain_json():
    raw = '[{"subject": "PM2.5", "relation": "utilise", "object": "Random Forest"}]'
    triples = parse_triples_response(raw)
    assert len(triples) == 1
    assert triples[0]["subject"] == "PM2.5"


def test_parse_triples_response_with_markdown_fences():
    raw = '```json\n[{"subject": "A", "relation": "relie", "object": "B"}]\n```'
    triples = parse_triples_response(raw)
    assert len(triples) == 1
    assert triples[0]["object"] == "B"


def test_parse_triples_response_invalid_json_returns_empty_list():
    raw = "Voici les triplets : pas du JSON valide"
    triples = parse_triples_response(raw)
    assert triples == []


def test_parse_triples_response_ignores_malformed_entries():
    raw = '[{"subject": "A", "relation": "x"}, {"subject": "B", "relation": "y", "object": "C"}]'
    triples = parse_triples_response(raw)
    # Le premier triplet est incomplet (pas de "object") et doit être ignoré
    assert len(triples) == 1
    assert triples[0]["subject"] == "B"


# ---- Tests de parsing (extraction d'entités) ----

def test_parse_entities_response_plain_json():
    raw = '["Projet PM2.5", "Federated Learning"]'
    entities = parse_entities_response(raw)
    assert entities == ["Projet PM2.5", "Federated Learning"]


def test_parse_entities_response_with_markdown_fences():
    raw = '```json\n["EventGuard"]\n```'
    entities = parse_entities_response(raw)
    assert entities == ["EventGuard"]


# ---- Tests de construction et requêtage du graphe ----

def _sample_triples():
    return [
        {"subject": "Projet PM2.5", "relation": "utilise", "object": "Random Forest", "source": "pm25.md"},
        {"subject": "Projet PM2.5", "relation": "entraîné avec", "object": "Flower", "source": "pm25.md"},
        {"subject": "EventGuard", "relation": "utilise", "object": "Azure Key Vault", "source": "eventguard.md"},
    ]


def test_build_graph_from_triples_creates_expected_nodes_and_edges():
    graph = build_graph_from_triples(_sample_triples())
    assert "Projet PM2.5" in graph.nodes
    assert "Random Forest" in graph.nodes
    assert graph.number_of_edges() == 3


def test_find_matching_nodes_case_insensitive_substring():
    graph = build_graph_from_triples(_sample_triples())
    matches = find_matching_nodes(graph, "pm2.5")
    assert "Projet PM2.5" in matches


def test_find_matching_nodes_no_match_returns_empty_list():
    graph = build_graph_from_triples(_sample_triples())
    matches = find_matching_nodes(graph, "Entité inexistante")
    assert matches == []


def test_format_triples_as_context_includes_relation_and_source():
    graph = build_graph_from_triples(_sample_triples())
    context = format_triples_as_context(graph, ["Projet PM2.5"])
    assert "utilise" in context
    assert "Random Forest" in context
    assert "pm25.md" in context


if __name__ == "__main__":
    test_parse_triples_response_plain_json()
    test_parse_triples_response_with_markdown_fences()
    test_parse_triples_response_invalid_json_returns_empty_list()
    test_parse_triples_response_ignores_malformed_entries()
    test_parse_entities_response_plain_json()
    test_parse_entities_response_with_markdown_fences()
    test_build_graph_from_triples_creates_expected_nodes_and_edges()
    test_find_matching_nodes_case_insensitive_substring()
    test_find_matching_nodes_no_match_returns_empty_list()
    test_format_triples_as_context_includes_relation_and_source()
    print("Tous les tests sont passés ✓")
