# Idées en vrac

## Index

- terme -> commentaires
- commentaire -> méta-données
- utilisateur -> commentaires
- thread -> commentaires
- subreddit -> posts
- post -> commentaires
- concept ODP -> commentaires


## Embedding

Embedding des utilisateurs dans l'espace des subreddits
  (user6: sub1 sub5 ... sub1924)

Embeddings documents:
- TF-IDF BoW: simple, rapide à calculer, représentatif du lexique (termes spécifique) mais pas de la sémantique
- Word2Vec aggrégé (somme/moyenne): 
- Doc2Vec: gourmand en ressources, à priori légèrement plus efficace qu'aggrégation des représentations de mots
- Fasttext: possibilité de traiter les fautes d'aurtograf et jargons
  
## Hiérarchies
Créer une hiérarchie des subreddits, à comparer/fit à la hiérarchie ODP ?

## Résumé
Résumé de concepts d'un document : les plus typiques d'un doc, en étant différent des concepts déjà choisis
