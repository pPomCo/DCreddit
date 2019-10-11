# A/B test

## Description

- Évaluation des systèmes personnalisés et non-personnalisés à l'aveugle.
 - Évaluation des méthode de réordonnancement des résultats à l'aveugle

Pour l'instant, le système personnalisé reçoit le nom d'utilisateur en argument : on ne peut le tester qu'en *se mettant à la place d'un utilisateur existant*.


## Utilisation

On peut appeler directement le script python *ab_app.py*, ou utiliser le script bash *ab_test.sh* qui lance un test A ou B au hasard. L'utilisateur n'est donc pas au courant (même s'il s'agit de l'un des programmeurs).  
Les résultats sont enregistrés dans le dossier *results/*, le nom du fichier étant *run_id*, il caractérise totalement une session.

	# Démarrer un test 
	# (A/B et le reordonnancement sont choisis aléatoirement)
	./ab_test.sh

Signature de *ab_app.py*:

	python3 ab_app.py -h
	> usage: ab_app.py [-h] [--sim [SIM]] dir run_id [author]
	>
	> Execute queries on comment body
	>
	> positional arguments:
	>   dir          Index directory
	>   run_id       AB_test run id
	>   author       Author (for personalized results)
	>
	> optional arguments:
	>   -h, --help   show this help message and exit
	>   --sim [SIM]  Similarity (in [tfidf, lm, bm25])
