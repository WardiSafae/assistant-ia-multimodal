"""
Génération de la réponse finale à partir du contexte récupéré (RAG ou graphe)
et de la question posée par l'utilisateur.

Le fournisseur LLM est configurable via les variables d'environnement
(voir .env.example) pour ne pas dépendre d'un seul fournisseur payant :
- "mistral" : API Mistral (ChatMistralAI, offre un quota gratuit)
- "openai_compatible" : tout endpoint compatible API OpenAI, y compris
  Ollama en local (gratuit, aucune clé API nécessaire)
"""



import os
import time

from dotenv import load_dotenv

load_dotenv()

PROMPT_TEMPLATE = """Tu es un assistant qui répond à des questions en te basant \
uniquement sur le contexte fourni ci-dessous. Si le contexte ne permet pas de \
répondre, dis-le clairement plutôt que d'inventer une réponse.

Contexte :
{context}

Question : {question}

Réponse concise et sourcée :"""

# Le quota gratuit Mistral est limité (~1 req/s) : on retente automatiquement
# en cas de 429 plutôt que de faire planter le pipeline.
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 5


def _get_llm():
    """
    Instancie le client LLM selon le fournisseur configuré dans .env.
    """
    provider = os.getenv("LLM_PROVIDER", "mistral")
    model = os.getenv("LLM_MODEL", "mistral-small-latest")
    api_key = os.getenv("LLM_API_KEY", "not-needed")

    if provider == "mistral":
        from langchain_mistralai import ChatMistralAI

        return ChatMistralAI(model=model, api_key=api_key, temperature=0.2)

    # Fallback générique compatible OpenAI (Ollama, vLLM, etc.)
    from langchain_openai import ChatOpenAI

    base_url = os.getenv("LLM_BASE_URL") or None
    return ChatOpenAI(
        model=model,
        api_key=api_key or "not-needed",
        base_url=base_url,
        temperature=0.2,
    )


def _extract_content(response) -> str:
    """
    Extrait proprement le texte de la réponse LLM.
    Gère les cas où le contenu est une liste de blocs (Mistral renvoie parfois
    une liste de dicts au lieu d'une simple chaîne).
    """
    content = response.content

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and "text" in block:
                parts.append(block["text"])
        return "".join(parts)

    return str(content)


def generate_answer(question: str, context: str) -> str:
    """
    Génère une réponse en langage naturel à partir de la question et du
    contexte récupéré (peu importe que ce contexte vienne du backend RAG
    vectoriel ou du backend graphe de connaissances — c'est ce qui rend le
    pipeline modulaire).

    Retente automatiquement en cas d'erreur de quota (429), avec un délai
    d'attente entre chaque tentative.
    """
    if not context or not context.strip():
        return "Je ne peux pas répondre : aucun contexte pertinent trouvé dans la base."

    llm = _get_llm()
    prompt = PROMPT_TEMPLATE.format(context=context, question=question)

    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = llm.invoke(prompt)
            return _extract_content(response)
        except Exception as error:
            last_error = error
            is_rate_limit = "429" in str(error) or "rate limit" in str(error).lower()
            if is_rate_limit and attempt < MAX_RETRIES:
                print(
                    f"Quota API atteint (tentative {attempt}/{MAX_RETRIES}), "
                    f"nouvelle tentative dans {RETRY_DELAY_SECONDS}s ..."
                )
                time.sleep(RETRY_DELAY_SECONDS)
                continue
            raise

    raise last_error


if __name__ == "__main__":
    demo_context = (
        "Le projet PM2.5 utilise un modèle Random Forest (R² = 0,966) "
        "entraîné de façon fédérée via Flower."
    )
    demo_question = "Quel framework a été utilisé pour l'apprentissage fédéré ?"
    print(generate_answer(demo_question, demo_context))
    