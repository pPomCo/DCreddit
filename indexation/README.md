# Indexation

## indexer.py

Comments indexation and querying. 

### Usage

    python3 indexer.py -h
    > usage: indexer.py [-h] DB [storeDir] [relation]
    
    > Build index on comments and users
    
    > positional arguments:
    >   DB          path of the sqlite3 database to index
    >   storeDir    path where to build index (default: 'index/')
    >   relation    Relation name (default: 'May2015')
    
    > optional arguments:
    >   -h, --help  show this help message and exit


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
