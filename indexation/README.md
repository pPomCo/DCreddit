# Indexation

## indexer.py

    python3 indexer.py -h
    > usage: indexer.py [-h] DB [storeDir] [relation]
    
    > Build index on comments and users
    
    > positional arguments:
    >   DB          path of the sqlite3 database to index
    >   storeDir    path where to build index (default: 'index/')
    >   relation    Relation name (default: 'May2015')
    
    > optional arguments:
    >   -h, --help  show this help message and exit
    >   --sim [SIM]  Similarity (in [tfidf, lm, bm25])


## searcher.py

    python3 searcher.py -h
    > usage: searcher.py [-h] dir
    > 
    > Execute queries on comment body
    >
    > positional arguments:
    >   dir         Index directory
    >
    > optional arguments:
    >   -h, --help  show this help message and exit
    >   --sim [SIM]  Similarity (in [tfidf, lm, bm25])
    >   --reorder [REORDER]  Reordering (in [ups, normups])
    >   --short              Don't show the body of comments


## get_term_vectors.py

    python3 get_term_vectors.py -h
    > usage: get_term_vectors.py [-h] [storeDir]
    >
    > Build index on comments and users
    >
    > positional arguments:
    >   storeDir    path where to build index (default: 'index/')
    >
    > optional arguments:
    >   -h, --help  show this help message and exit
