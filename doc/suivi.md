# Document de suivi

## Tâches

| Sprint | Échéance | Tâche |
| :---: | :---: | --- |
| n°1 | 03/10 | Indexation v0 : workflow simple (modèle vectoriel) |
| n°2 | 07/10 | Moteur RI (non perso), exploration données, début tâche suivante |

## Détail

### Semaine 40

#### Lundi 30/09

- **Compréhension du sujet**
    - Indexation des commentaires et plus
    - Finalités :
        - Réponses personnalisée à des requêtes
        - Accès rapide aux features pour l'apprentissage
- **Organisation générale**
    - Deux sprints par semaine
    - Coordination avec les autres groupes : à faire

- **Objectifs identifiés**
    - Exploration des données (structure) + réalisation d'un sample
    - Réalisation d'un workflow simple (indexation des commentaires)
        - Modèle vectoriel (TFxIDF)
        - PyLucene
    - Confirmation de la démarche de gestion de projet
    
#### Mardi 01/10

- **Tâches**
    - Création d'un échantillon des données
    - Création d'un premier index (terms -> comments)
    - Reflexion : quels index réaliser pour le sprint 2 ?
    
- **Identification issues**
    - Déploiement (moteur d'accès) -> interfaçage avec les autres groupes
        - Première discussion avec les autres groupes (pas de réponses)
    - Technos (pylucene) -> libre
    - Gestion données temporelles -> indexées en tant que méta-données du document

#### Mercredi 02/10 et jeudi 03/10

- **Tâches**
    - Exploration des données
    - Indexation sur Osirim
    - Modèles vectoriels, probabilistes, de langue
    - Reordonnancement des résultats selon 'ups' (non personnalisé)
    
#### Vendredi 04/10
- **Tâches**
    - Concertation concernant l'interfaçage avec les autres groupes
    - Construction d'un profil utilisateur basique
    - Mise en place d'un modèle prédictif basique
    
- **Problèmes**
    - Représentation partagée entre commentaires et concepts ODP ?
    - Comment utiliser l'ensemble des données (commentaire à prédire + reste du thread/subreddit ?) pour la prédiction ?
    - Comment évaluer la pertinence d'un document ? Quelle est la vérité terrain ? Les requêtes types ?
        - Si on utilise le score pour évaluer la pertinence, on ne peut plus s'en servir pour évaluer la performance du système...


#### Lundi 07/10
- **Tâches**
    - Requêtes personnalisées (reformulation de requête considérant le profil basique)
    - Évaluation système : requêtes aléatoires + présentation résultats

#### Mardi 08/10
- **Tâches**
    - Mise en place du protocole d'évaluations des features
    - Lancement de l'indexation sur la plateforme osirim
    - Etudes des représentations vectorielles de documents (embeddings)
