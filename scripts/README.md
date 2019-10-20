# Embeddings

## embeddings.py
```js
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

```js
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

