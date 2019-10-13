"""
Execute query on comments -- results are personalized
Using query reformulation

Actually it's working, but seems to be less relevant than the not-personalized
approch.

Querying can be automated by piping a query-file into this program. Each line
is a query, and an empty line (at least the last) stops the program.

Can set the representation model (TK-IDF, LM, BM25) depending on the index.
"""

import user_profile as up_lib
import searcher as s_lib
import sys, os, lucene, threading, time

from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.search import IndexSearcher, BoostQuery, BooleanQuery
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.search.similarities import \
     ClassicSimilarity, LMDirichletSimilarity, BM25Similarity


N_DOCS = 10


def escape_lucene_special_chars(string):
    for c in ['//', '+', '-', '&&', '||', '!', '(', ')', '{', '}', '[', ']',
              '^', '"', '~', '*', '?', ':', '/']:
        string = string.replace(c, ' ')
    return string



def reformulate_query(initial_query, searcher, analyzer, user_name):
    """reformulate query using profile similarity"""
    
    profile = up_lib.user_profile(searcher, user_name)

    # Vocabulary of his own comments
    q_comm = QueryParser("name", analyzer).parse(" ".join(profile['comments']))
    scoreDocs = searcher.search(q_comm, 1000).scoreDocs
    w_comm = " ".join([searcher.doc(sd.doc).get('body') for sd in scoreDocs])

    # Vocabulary of the links he posts on
    q_link = QueryParser("link_id", analyzer).parse(" ".join(profile['links']))
    scoreDocs = searcher.search(q_link, 1000).scoreDocs
    w_link = " ".join([searcher.doc(sd.doc).get('body') for sd in scoreDocs])

    # Vocabulary of the subreddit he posts on
    q_subr = QueryParser("subreddit", analyzer).parse(" ".join(profile['subreddits']))
    scoreDocs = searcher.search(q_link, 1000).scoreDocs
    w_subr = " ".join([searcher.doc(sd.doc).get('body') for sd in scoreDocs])

    # Print vocabularies
##    print("\nComments vocabulary:", w_comm)
##    print("\nLinks vocabulary:", w_link)
##    print("\nSubreddits vocabulary:", w_subr)


    # Reformulated query. Weights are not justified
    reformulated_query = QueryParser("body", analyzer).parse(
        "(%s)^1 (%s)^0.05 (%s)^0.03 (%s)^0.02"%(
            escape_lucene_special_chars(initial_query),
            escape_lucene_special_chars(w_comm),
            escape_lucene_special_chars(w_link),
            escape_lucene_special_chars(w_subr)
            ))

    return reformulated_query




def run(searcher, analyzer, user_name, reordering='no', show_bodies=True):
    while True:
        print()
        print("Hit enter with no input to quit.")
        command = input("Query:")
        if command == '':
            return

        print()
        print("Searching for:", command)

        # Query reformulation
        query = reformulate_query(command, searcher, analyzer, user_name)
        
        scoreDocs = searcher.search(query, N_DOCS).scoreDocs
        print("%s total matching documents." % len(scoreDocs))


        if reordering == 'ups':
            scoreDocs, scores = s_lib.reorder_ups(scoreDocs, searcher)
        elif reordering == 'normups':
            scoreDocs, scores = s_lib.reorder_normups(scoreDocs, searcher)
        else:
            n_docs = len(scoreDocs)
            scores = {sd.doc: (n_docs-i,) for i,sd in enumerate(scoreDocs)}

        # Print results
        for i, scoreDoc in enumerate(scoreDocs):
            doc = searcher.doc(scoreDoc.doc)
            print("%d: %s [by %s] (score: %s)"%(
                i,
                doc.get('name'),
                doc.get('author'),
                "%s=%.3f"%(
                    "+".join(["%.3f"%x for x in scores[scoreDoc.doc]]),
                    sum(scores[scoreDoc.doc])
                    )
                ))
            if not show_bodies:
                print(doc.get('body'), "\n")

        


if __name__ == "__main__":

    # Init lucene
    lucene.initVM()

    
    # Read command-line arguments
    import argparse
    parser = argparse.ArgumentParser(
        description='Execute queries on comment body')
    parser.add_argument('user_name', type=str,
                        help="User name (profile to use)")
    parser.add_argument('index_dir', metavar='dir', type=str,
                        help="Index directory")
    parser.add_argument('--sim', type=str, nargs='?',
                        default="tfidf", help="Similarity (in [tfidf, lm, bm25])")
    parser.add_argument('--reorder', type=str, nargs='?',
                        default="no", help="Reordering (in [ups, normups])")
    parser.add_argument('--short', action='store_false',
                        help="Don't show the body of comments")
    args = parser.parse_args()


    if args.sim in ['bm25']:
        similarity = BM25Similarity()
    elif args.sim in ['lm']:
        similarity = LMDirichletSimilarity()
    else:
        similarity = ClassicSimilarity()

    # Sample query
    storeDir = SimpleFSDirectory(Paths.get(args.index_dir))
    searcher = IndexSearcher(DirectoryReader.open(storeDir))
    if similarity is not None:
        searcher.setSimilarity(similarity)
    analyzer = StandardAnalyzer()
    run(searcher, analyzer, args.user_name, reordering=args.reorder, show_bodies=not args.short)
