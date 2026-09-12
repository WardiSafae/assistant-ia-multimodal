"""
Construction du graphe de connaissances à partir du corpus.

Approche : pour chaque document, on demande au LLM d'extraire des triplets
(sujet, relation, objet), puis on assemble ces triplets en un graphe orienté
NetworkX. C'est une version simplifiée mais fonctionnelle d'une problématique
classique de recherche appliquée en IA : conception et exploitation de
graphes de connaissances, intégration de modèles avancés (LLMs) pour
améliorer l'accès et la compréhension de l'information.

À exécuter une fois avant d'utiliser le backend graphe :
    python -m src.backends.knowledge_graph.build_graph
"""

import glob
import json
import os
import pickle
import re

GRAPH_DIR = os.path.join(os.path.dirname(__file__), "index")
CORPUS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "corpus")

EXTRACTION_PROMPT = """Extrait les faits importants du texte ci-dessous sous forme de triplets (sujet, relation, objet) en français.

RÈGLES ABSOLUES :
- Réponds UNIQUEMENT avec une liste JSON valide. AUCUN texte avant ou après.
- N'écris PAS les règles, N'explique PAS, N'ajoute PAS de commentaires.
- Format exact : [{{"subject": "...", "relation": "...", "object": "..."}}]
- Maximum 8 triplets.
- Le sujet et l'objet sont des entités COURTES (2 à 5 mots MAXIMUM).
- La relation est un verbe court (ex: "utilise", "obtient", "fait partie de").
- Ne répète pas les mêmes informations dans plusieurs triplets.

EXEMPLE :
Texte : "Le projet X utilise Python et obtient un R² de 0.95."
Réponse : [{{"subject": "projet X", "relation": "utilise", "object": "Python"}}, {{"subject": "projet X", "relation": "obtient", "object": "R² de 0.95"}}]

Texte à analyser :
{text}

JSON :"""


def parse_triples_response(raw_response: str) -> list[dict]:
    """
    Parse la réponse du LLM (censée être une liste JSON de triplets) de façon
    robuste : le LLM entoure parfois sa réponse de balises markdown (```json ... ```)
    malgré la consigne — on nettoie avant de parser.

    Ne dépend d'aucun appel réseau : testable isolément (voir tests/).
    """
    cleaned = raw_response.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        triples = json.loads(cleaned)
    except json.JSONDecodeError:
        return []

    valid_triples = [
        t for t in triples
        if isinstance(t, dict) and {"subject", "relation", "object"} <= t.keys()
    ]
    return valid_triples


def build_graph_from_triples(triples: list[dict]):
    """
    Construit un graphe orienté NetworkX à partir d'une liste de triplets.
    Chaque arête porte la relation et, si fournie, la source du document.

    Ne dépend d'aucun appel réseau : testable isolément (voir tests/).
    """
    import networkx as nx

    graph = nx.MultiDiGraph()
    for triple in triples:
        subject = triple["subject"].strip()
        obj = triple["object"].strip()
        relation = triple["relation"].strip()
        source = triple.get("source", "inconnu")
        graph.add_edge(subject, obj, relation=relation, source=source)
    return graph


def extract_triples_from_document(text: str, source: str) -> list[dict]:
    """Appelle le LLM pour extraire les triplets d'un document donné."""
    from src.generation.generate_answer import _extract_content, _get_llm

    llm = _get_llm()
    prompt = EXTRACTION_PROMPT.format(text=text)
    response = llm.invoke(prompt)

    triples = parse_triples_response(_extract_content(response))
    for triple in triples:
        triple["source"] = source
    return triples


def build_graph(corpus_dir: str = CORPUS_DIR, graph_dir: str = GRAPH_DIR) -> None:
    """
    Parcourt tous les documents du corpus, extrait les triplets via le LLM,
    construit le graphe de connaissances et le sauvegarde sur disque.
    """
    os.makedirs(graph_dir, exist_ok=True)

    all_triples = []
    filepaths = sorted(glob.glob(os.path.join(corpus_dir, "*.md")))
    print(f"{len(filepaths)} documents trouvés dans {corpus_dir}")

    for filepath in filepaths:
        source_name = os.path.basename(filepath)
        print(f"Extraction des triplets pour {source_name} ...")
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        triples = extract_triples_from_document(content, source_name)
        print(f"  → {len(triples)} triplets extraits")
        all_triples.extend(triples)

    graph = build_graph_from_triples(all_triples)
    print(f"\nGraphe construit : {graph.number_of_nodes()} nœuds, {graph.number_of_edges()} relations")

    with open(os.path.join(graph_dir, "knowledge_graph.pkl"), "wb") as f:
        pickle.dump(graph, f)

    # Export lisible en complément, utile pour inspecter le graphe sans code
    with open(os.path.join(graph_dir, "triples.json"), "w", encoding="utf-8") as f:
        json.dump(all_triples, f, ensure_ascii=False, indent=2)

    print(f"Graphe sauvegardé dans {graph_dir}/")


if __name__ == "__main__":
    build_graph()
