# Features extraction

If we cannot acces Neo4j database...

	# link_id -> top-k child comments (score=ups)
	k=10
	python3 link_child_comments.py $k
	
	# comment -> ancestor comments
	python3 comment_ancestors.py
	
	# comment -> previous brother comments
	python3 anterior_comments.py
	
	# user -> n_comments, total_n_ups
	python3 user_info.py
	
	# All
	make

Each python script prints a CSV-like document