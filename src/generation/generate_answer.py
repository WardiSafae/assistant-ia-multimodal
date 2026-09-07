"""
Génération de la réponse finale à partir du contexte récupéré (RAG ou graphe)
et de la question posée par l'utilisateur.

Le fournisseur LLM est configurable via les variables d'environnement
(voir .env.example) pour ne pas dépendre d'un seul fournisseur payant :
- "mistral" : API Mistral (offre un quota gratuit)
- "openai_compatible" : tout endpoint compatible API OpenAI, y compris
  Ollama en local (gratuit, aucune clé API nécessaire)
"""

import os

from dotenv import load_dotenv
from langchain_community.chat_models import ChatOpenAI

load_dotenv()

PROMPT_TEMPLATE = """Tu es un assistant qui répond à des questions en te basant \
uniquement sur le contexte fourni ci-dessous. Si le contexte ne permet pas de \
répondre, dis-le clairement plutôt que d'inventer une réponse.

Contexte :
{context}

Question : {question}

Réponse concise et sourcée :"""


def _get_llm():
    """
    Instancie le client LLM selon le fournisseur configuré dans .env.
    Utilise l'interface compatible OpenAI de LangChain, qui fonctionne aussi
    bien avec Mistral, Ollama en local, ou tout autre endpoint compatible.
    """
    provider = os.getenv("LLM_PROVIDER", "mistral")
    model = os.getenv("LLM_MODEL", "mistral-small-latest")
    api_key = os.getenv("LLM_API_KEY", "not-needed")
    base_url = os.getenv("LLM_BASE_URL") or None

    if provider == "mistral" and not base_url:
        base_url = "https://api.mistral.ai/v1"

    return ChatOpenAI(
        model=model,
        api_key=api_key,
        base_url=base_url,
        temperature=0.2,
    )


def generate_answer(question: str, context: str) -> str:
    """
    Génère une réponse en langage naturel à partir de la question et du
    contexte récupéré (peu importe que ce contexte vienne du backend RAG
    vectoriel ou du backend graphe de connaissances — c'est ce qui rend le
    pipeline modulaire).
    """
    llm = _get_llm()
    prompt = PROMPT_TEMPLATE.format(context=context, question=question)
    response = llm.invoke(prompt)
    return response.content


if __name__ == "__main__":
    demo_context = "Le projet PM2.5 utilise un modèle Random Forest (R² = 0,966) entraîné de façon fédérée via Flower."
    demo_question = "Quel framework a été utilisé pour l'apprentissage fédéré ?"
    print(generate_answer(demo_question, demo_context))
