from dotenv import load_dotenv
from src.generation.generate_answer import _get_llm, _extract_content

load_dotenv()

llm = _get_llm()

prompt = """Extrait les faits importants du texte ci-dessous sous forme de triplets (sujet, relation, objet), en français, concis.

Règles :
- Le sujet et l'objet doivent être des entités courtes.
- La relation doit être un verbe ou une expression courte.
- Réponds UNIQUEMENT avec une liste JSON, sans texte autour, au format :
[{"subject": "...", "relation": "...", "object": "..."}, ...]

Texte :
Le projet PM2.5 utilise un modèle Random Forest entraîné de façon fédérée via Flower.

Liste JSON de triplets :"""

response = llm.invoke(prompt)
print("=== RÉPONSE BRUTE ===")
print(repr(response.content))
print("\n=== CONTENU EXTRAIT ===")
print(_extract_content(response))