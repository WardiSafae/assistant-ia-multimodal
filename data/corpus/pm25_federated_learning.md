# Projet PM2.5 — Prédiction de la qualité de l'air par apprentissage fédéré

## Contexte
Projet réalisé dans le cadre du module "Explorer l'IA et l'apprentissage fédéré"
du Master Big Data et Systèmes Intelligents (BDSI), FSDM, USMBA.

## Objectif
Prédire la concentration de PM2.5 (particules fines) et classifier l'indice de
qualité de l'air (AQI) sur six villes marocaines, en utilisant un entraînement
fédéré plutôt qu'une centralisation des données.

## Méthode
- Modèle de régression : Random Forest, obtenant un R² de 0,966 pour la
  prédiction du PM2.5.
- Classification de l'AQI : exactitude de 98,5%.
- Entraînement fédéré via le framework Flower : chaque ville entraîne le
  modèle localement sur ses propres données, seuls les paramètres du modèle
  sont partagés et agrégés, jamais les données brutes.
- Performance par ville très variable (R² allant de -0,40 à 0,78 selon les
  villes), ce qui a nécessité une analyse critique des causes : hétérogénéité
  des données locales, volumes différents, qualité des capteurs.

## Résultat clé
Le projet démontre qu'il est possible d'obtenir un modèle prédictif performant
sans jamais centraliser les données sensibles de capteurs environnementaux,
tout en documentant précisément les limites de l'approche selon les scénarios.
