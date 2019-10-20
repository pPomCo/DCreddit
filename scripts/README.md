# Embeddings

## embeddings.py
```
> python3 embeddings.py -h
usage: embeddings.py [-h] [-db DB] [-c] [-s] [-u]

Create clusters and user profiles from database. Paths for resources at top of
the code.

optional arguments:
  -h, --help        show this help message and exit
  -db DB            Database path to read users and comments
  -c, --comments    Create CSV file with all comments embeddings.
  -s, --subreddits  Find clusters and save variables with the embeddings for
                    each one.
  -u, --users       Create file with all user themes embeddings.

````

## social.py

```
>python3 social.py -h
usage: social.py [-h] [-db DB] [-m] [-r]

Create social vector user profiles from database. Paths for resources at top
of the code.

optional arguments:
  -h, --help    show this help message and exit
  -db DB        Database path to read users and comments.
  -m, --matrix  Compute the social matrix (response ratio) between users.
  -r, --recomm  Returns a list of recommended user to follow for each user.
```

## searcher.py
```
>python3 searcher.py -h
usage: searcher.py [-h] [--ndocs [NDOCS]] [--sim [SIM]] [--reorder [REORDER]]
                   [--user [USER]] [--testFile [TESTFILE]] [--short]
                   dir

Execute personalised queries on comment body

positional arguments:
  dir                   Index directory

optional arguments:
  -h, --help            show this help message and exit
  --ndocs [NDOCS]       Number of documents to return for each query
  --sim [SIM]           Similarity (in [tfidf, lm, bm25])
  --reorder [REORDER]   Reordering (in [ups, normups, profile])
  --user [USER]         User to pick from database
  --testFile [TESTFILE]
                        Path of qrel file
  --short               Don't show the body of comments

```
