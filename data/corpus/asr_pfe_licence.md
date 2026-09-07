# PFE Licence — Corpus audio pour la reconnaissance automatique de la parole arabe

## Contexte
Projet de fin d'études de la Licence Fondamentale Sciences Mathématiques et
Informatique (SMI), FSDM, USMBA.

## Objectif
Créer un corpus audio en langue arabe destiné à l'entraînement d'un système
de reconnaissance automatique de la parole (ASR / Speech-to-Text).

## Méthode
- Collecte et enregistrement d'un corpus audio en arabe.
- Segmentation phonétique des enregistrements.
- Entraînement d'un modèle acoustique combinant réseaux de neurones
  convolutionnels et récurrents (CNN + LSTM).
- Décodage des séquences via l'algorithme de Viterbi.

## Prolongements en Master
Ce travail a été approfondi en Master via :
- le module Reconnaissance Automatique de la Parole (approches Modèles de
  Markov Cachés — HMM, Viterbi, Baum-Welch — comparées aux architectures
  neuronales de bout en bout comme Wav2Vec2-XLSR-53) ;
- un second projet de modélisation acoustique CNN+LSTM (194K paramètres),
  atteignant 63% d'exactitude sur un jeu de test dédié.

## Résultat clé
Une double compétence rare : compréhension théorique des fondements du
traitement de la parole (HMM, modèles neuronaux) et expérience pratique de
bout en bout, de la constitution du corpus à l'évaluation du modèle.
