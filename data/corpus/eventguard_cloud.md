# Projet EventGuard — Plateforme cloud sécurisée

## Contexte
TP réalisé dans le cadre du module Cybersécurité et Cloud Computing du Master
BDSI, portant sur la sécurisation d'une application cloud sur Microsoft Azure.

## Objectif
Concevoir une application web (architecture MVC, Java/Spring Boot) intégrant
les bonnes pratiques de sécurité cloud pour la gestion d'événements.

## Méthode
- Authentification forte via Azure Entra ID et authentification multi-facteurs
  (MFA/TOTP).
- Gestion sécurisée des secrets applicatifs via Azure Key Vault (aucun secret
  en clair dans le code ou la configuration).
- Hachage des mots de passe avec BCrypt.
- Hébergement sur Azure App Service, base de données PostgreSQL.

## Résultat clé
Le projet illustre une chaîne de sécurité complète : de la gestion des secrets
à l'authentification utilisateur, en passant par le chiffrement des données
sensibles — une base directement transférable à des problématiques de
confidentialité des données dans un contexte professionnel.
