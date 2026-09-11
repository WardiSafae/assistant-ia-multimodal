# Rapport d'évaluation d'un système Text-to-Speech

*Généré le 11/09/2026 à 19:11*

## 1. Méthodologie

Chaque phrase de test est synthétisée par le système TTS, puis retranscrite par un système de reconnaissance vocale indépendant (Whisper). L'écart entre le texte d'origine et la transcription obtenue (Word Error Rate, WER) sert de proxy à l'intelligibilité de la synthèse : plus le WER est faible, plus la synthèse est jugée fidèle et compréhensible.

**Seuil de conformité retenu pour ce projet : WER ≤ 15%** (seuil indicatif, à ajuster selon le contexte réel d'usage — un système opérant en environnement réglementé exigerait une analyse de risque dédiée et probablement des seuils différenciés par catégorie de criticité).

Les phrases de test sont réparties en catégories représentatives de difficultés connues en synthèse vocale : phrases courtes/longues, chiffres, sigles/acronymes, noms propres, homographes ambigus.

## 2. Résultats par catégorie

| Catégorie | Nb tests | WER moyen | Taux de conformité |
|---|---|---|---|
| phrases_courtes | 3 | 0.0% | 100% |
| phrases_longues | 2 | 10.0% | 50% |
| chiffres_et_nombres | 3 | 34.9% | 0% |
| sigles_et_acronymes | 3 | 35.1% | 33% |
| noms_propres | 2 | 12.5% | 50% |
| homographes_ambigus | 2 | 5.0% | 100% |

## 3. Détail des tests

### phrases_courtes — verdict : Conforme (WER = 0.0%)
- **Texte de référence** : Bonjour, comment allez-vous ?
- **Texte retranscrit** : Bonjour, comment allez-vous ?

### phrases_courtes — verdict : Conforme (WER = 0.0%)
- **Texte de référence** : Le vol est prêt au décollage.
- **Texte retranscrit** : Le vol est prêt au décollage.

### phrases_courtes — verdict : Conforme (WER = 0.0%)
- **Texte de référence** : Merci de votre attention.
- **Texte retranscrit** : Merci de votre attention.

### phrases_longues — verdict : Non conforme (WER = 20.0%)
- **Texte de référence** : La direction technique et ingénierie assure le développement, la conception et le suivi des équipements associés dans le respect des normes de sécurité en vigueur.
- **Texte retranscrit** : La direction technique est ingénirie à sûr le développement. La conception est le suivi des équipements associés dans le respect des normes de sécurité en vigueur.

### phrases_longues — verdict : Conforme (WER = 0.0%)
- **Texte de référence** : Après plusieurs vérifications successives, l'équipe a confirmé que l'ensemble des paramètres de vol restait conforme aux valeurs attendues durant toute la phase de croisière.
- **Texte retranscrit** : Après plusieurs vérifications successives, l'équipe a confirmé que l'ensemble des paramètres de vol restait conforme aux valeurs attendues. Durant toute la phase de croisière.

### chiffres_et_nombres — verdict : Non conforme (WER = 42.9%)
- **Texte de référence** : Le vol décolle à 22 heures 29.
- **Texte retranscrit** : le vol décolle à 22h29.

### chiffres_et_nombres — verdict : Non conforme (WER = 28.6%)
- **Texte de référence** : L'altitude de croisière est de 11000 mètres.
- **Texte retranscrit** : L'altitude de croisière est de 11 000 mètres.

### chiffres_et_nombres — verdict : Non conforme (WER = 33.3%)
- **Texte de référence** : La température extérieure est de moins 54 degrés Celsius.
- **Texte retranscrit** : La température extérieure est de moins 54°C.

### sigles_et_acronymes — verdict : Non conforme (WER = 50.0%)
- **Texte de référence** : Le système ILS permet l'atterrissage automatique.
- **Texte retranscrit** : Le système il permet la thérissage automatique.

### sigles_et_acronymes — verdict : Conforme (WER = 12.5%)
- **Texte de référence** : L'OACI fixe les normes internationales de navigation aérienne.
- **Texte retranscrit** : l'OACI fixe les normes internationales de navigation aériennes.

### sigles_et_acronymes — verdict : Non conforme (WER = 42.9%)
- **Texte de référence** : Le contrôleur ATC a autorisé la descente.
- **Texte retranscrit** : le contrôleur attaissé à autoriser la descente.

### noms_propres — verdict : Conforme (WER = 0.0%)
- **Texte de référence** : L'avion a décollé de l'aéroport Roissy Charles de Gaulle.
- **Texte retranscrit** : L'avion a décollé de l'aéroport Roissy Charles de Gaulle.

### noms_propres — verdict : Non conforme (WER = 25.0%)
- **Texte de référence** : Le moteur CFM56 équipe de nombreux avions moyen-courriers.
- **Texte retranscrit** : Le moteur CFM56 équipe de nombreux avions moyen courrier.

### homographes_ambigus — verdict : Conforme (WER = 0.0%)
- **Texte de référence** : Les poules du couvent couvent leurs œufs.
- **Texte retranscrit** : Les poules du couvent couvent leurs œufs.

### homographes_ambigus — verdict : Conforme (WER = 10.0%)
- **Texte de référence** : Il est plus de dix heures, nous sommes en retard.
- **Texte retranscrit** : Il est plus de 10 heures, nous sommes en retard.

## 4. Recommandations

- La catégorie la plus problématique est **sigles_et_acronymes** (WER moyen de 35.1%) : c'est un axe d'amélioration prioritaire pour le système testé.
- Ce protocole reste une preuve de concept : une méthodologie de certification réelle nécessiterait un jeu de test bien plus large, une évaluation humaine complémentaire (le WER seul ne capture pas la prosodie ni le naturel de la voix), et une analyse de robustesse face au bruit ou à des conditions dégradées.
