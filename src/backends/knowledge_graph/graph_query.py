"""
Backend graphe de connaissances.

Expose la même interface que le backend RAG vectoriel :
    query(question: str) -> str   (contexte pertinent pour répondre à la question)

Fonctionnement : le LLM extrait les entités mentionnées dans la question,
celles-ci sont recherchées dans le graphe (correspondance approximative), et
les relations impliquant ces entités (et leurs voisins directs) forment le
contexte transmis au LLM de génération.

C'est une version simplifiée d'un moteur de requêtage en langage naturel sur
un graphe de connaissances.
"""

import json
import os
import pickle
import re

from .build_graph import GRAPH_DIR

ENTITY_EXTRACTION_PROMPT = """Extrait les entités (noms propres, concepts clés) \
mentionnées dans la question suivante. Réponds UNIQUEMENT avec une liste JSON \
de chaînes de caractères, sans texte autour, par exemple : ["Entité 1", "Entité 2"]

Question : {question}

Liste JSON d'entités :"""


def parse_entities_response(raw_response: str) -> list[str]:
    """
    Parse la réponse du LLM (liste JSON d'entités), en nettoyant les
    éventuelles balises markdown. Ne dépend d'aucun appel réseau : testable
    isolément (voir tests/).
    """
    cleaned = raw_response.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        entities = json.loads(cleaned)
    except json.JSONDecodeError:
        return []

    return [e for e in entities if isinstance(e, str) and e.strip()]


def find_matching_nodes(graph, entity: str) -> list[str]:
    """
    Recherche approximative (insensible à la casse, sous-chaîne) des nœuds du
    graphe correspondant à une entité extraite de la question.

    Ne dépend d'aucun appel réseau : testable isolément (voir tests/).
    """
    entity_lower = entity.lower().strip()
    matches = []
    for node in graph.nodes:
        node_lower = node.lower()
        if entity_lower in node_lower or node_lower in entity_lower:
            matches.append(node)
    return matches


def format_triples_as_context(graph, nodes: list[str]) -> str:
    """
    Formate les relations (arêtes) impliquant les nœuds donnés en texte lisible,
    destiné à servir de contexte pour le LLM de génération.
    """
    lines = []
    seen = set()

    for node in nodes:
        for _, target, data in graph.out_edges(node, data=True):
            key = (node, data.get("relation"), target)
            if key in seen:
                continue
            seen.add(key)
            source = data.get("source", "inconnu")
            lines.append(f"{node} --[{data.get('relation')}]--> {target}  (source : {source})")

        for source_node, _, data in graph.in_edges(node, data=True):
            key = (source_node, data.get("relation"), node)
            if key in seen:
                continue
            seen.add(key)
            source = data.get("source", "inconnu")
            lines.append(f"{source_node} --[{data.get('relation')}]--> {node}  (source : {source})")

    return "\n".join(lines)


class KnowledgeGraphBackend:
    """Backend graphe de connaissances : requêtage en langage naturel via extraction d'entités."""

    def __init__(self, graph_dir: str = GRAPH_DIR):
        graph_path = os.path.join(graph_dir, "knowledge_graph.pkl")

        if not os.path.exists(graph_path):
            raise FileNotFoundError(
                "Graphe introuvable. Lancez d'abord : "
                "python -m src.backends.knowledge_graph.build_graph"
            )

        with open(graph_path, "rb") as f:
            self.graph = pickle.load(f)

    def query(self, question: str) -> str:
        """
        Extrait les entités de la question, les recherche dans le graphe, et
        renvoie les relations trouvées comme contexte pour le LLM.
        """
        from src.generation.generate_answer import _extract_content, _get_llm

        llm = _get_llm()
        prompt = ENTITY_EXTRACTION_PROMPT.format(question=question)
        response = llm.invoke(prompt)
        entities = parse_entities_response(_extract_content(response))

        matched_nodes = []
        for entity in entities:
            matched_nodes.extend(find_matching_nodes(self.graph, entity))
        matched_nodes = list(dict.fromkeys(matched_nodes))

        if not matched_nodes:
            return ""

        return format_triples_as_context(self.graph, matched_nodes)


if __name__ == "__main__":
    backend = KnowledgeGraphBackend()
    context = backend.query("Qu'est-ce que le projet PM2.5 ?")
    print(context)
