"""
Generate a random "ground truth" from the dataset

usage:
    python3 mk_ground_truth.py db nqr nkw

Produces *nqr* queries of *nkw* words picked in random comments, which are
likely to be expected as result for their corresponding queries

output format:
    comment_name [tab] word1 [space] word2 [space] ...

"""
import random

def escape_lucene_special_chars(string):
    for c in ['\\', '+', '-', '&', '|', '!', '(', ')', '{', '}', '[', ']',
              '^', '"', '~', '*', '?', ':', '/']:
        string = string.replace(c, ' ')
    return string


def mk_gtruth(documents, n_keywords):
    """Select n_keywords random words (print in a csv-like format)"""
    for name, body in documents:
        keywords = escape_lucene_special_chars(body).lower().split()
        random.shuffle(keywords)
        print("%s\t%s"%(name, " ".join(keywords[:n_keywords])))


if __name__ == "__main__":

    # Read commend-line arguments
    import argparse
    parser = argparse.ArgumentParser(
        description='Generate a grund truth by creating queries with n random words of a comment')
    parser.add_argument('db', type=str, help='sqlite3 database')
    parser.add_argument('nqr', type=int, help='number of queries')
    parser.add_argument('nkw', type=int, help='number of keywords per query')

    args = parser.parse_args()


    # Open DB
    import sqlite3
    conn = sqlite3.connect(args.db)
    c = conn.cursor()

    # Select random comments
    sql_query = """SELECT name, body FROM May2015 WHERE length(body) > 100 ORDER BY RANDOM() LIMIT %d""" % args.nqr
    comments = c.execute(sql_query)

    # Work
    mk_gtruth(comments, args.nkw)
