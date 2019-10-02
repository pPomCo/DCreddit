# Indexation

### indexer.py

Comments indexation

#### Usage

    python3 indexer.py -h
    > usage: indexer.py [-h] DB [storeDir] [relation]
    
    > Build index on comments and users
    
    > positional arguments:
    >   DB          path of the sqlite3 database to index
    >   storeDir    path where to build index (default: 'index/')
    >   relation    Relation name (default: 'May2015')
    
    > optional arguments:
    >   -h, --help  show this help message and exit
