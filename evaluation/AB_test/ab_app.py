"""
A/B test

We have to user existing users for personalization!

The app is parametrized by the run_id
run_id format:
    X_Y_Z
    X = A (not personalized app) or B (personalized app)
    Y (reordering) = no, ups or normups
    Z (id) = any characters

We can already test A_no_.+, A_ups_.+ and A_normups_.+, but as we have to use
existing users for the B test, we cannot test it for real.

TODO: add a first-step-run where profile is learned from user interactions?

"""

import lib.user_profile as lib_up
import lib.reordering as lib_r

import sys, os, lucene, threading, time

from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.search.similarities import \
     ClassicSimilarity, LMDirichletSimilarity, BM25Similarity


N_DOCS = 5


def build_query(command, searcher, analyzer, run_id):
    """Build a query depending on the run id"""
    query_mode = run_id.split('_')[0].lower()
    if query_mode == 'a':
        return QueryParser("body", analyzer).parse(command)
    if query_mode == 'b':
        return lib_up.reformulate_query(command, searcher, analyzer, run_id)
    raise ValueError("run_id=%s is not a valid run_id"%run_id)

def reorder(scoreDocs, searcher, run_id):
    """Reorder results depending on the run id"""
    try:
        reorder_mode = run_id.split('_')[1].lower()
    except IndexError:
        raise ValueError("run_id=%s is not a valid run_id"%run_id)

    if reorder_mode == "no":
        return lib_r.reorder_null(scoreDocs, searcher)
    if reorder_mode == "ups":
        return lib_r.reorder_ups(scoreDocs, searcher)
    if reorder_mode == "normups":
        return lib_r.reorder_normups(scoreDocs, searcher)
    raise ValueError("run_id=%s is not a valid run_id"%run_id)


def run(searcher, analyzer, run_id):
    
    while True:
        print()
        print("Hit enter with no input to quit.")
        command = input("Query:")
        if command == '':
            return

##        command = escape_lucene_special_chars(command)
        print()
        print("Searching for:", command)
        query = build_query(command, searcher, analyzer, run_id)
        scoreDocs = searcher.search(query, N_DOCS).scoreDocs
        scoreDocs, scores = reorder(scoreDocs, searcher, run_id)


        # Print results 1-by-1, ask user to evaluate relevence
        for i, scoreDoc in enumerate(scoreDocs):
            doc = searcher.doc(scoreDoc.doc)
            print("%d: %s"%(
                i,
                doc.get('name'),
                ))
            print(doc.get('body'), "\n")

            # User score (0 to 5)
            star_score = -1
            print()
            while not star_score in [0,1,2,3,4,5]:
                star_score = input("Please rate this result with 0 to 5 stars [0-5]:")
                try:
                    star_score = int(star_score)
                except ValueError:
                    star_score = -1

            # Log score
            with open(os.path.join('results','%s.txt'%run_id), 'a') as f:
                print(command,
                      i,
                      doc.get('name'),
                      "%s=%.3f"%(
                          "+".join(["%.3f"%x for x in scores[scoreDoc.doc]]),
                          sum(scores[scoreDoc.doc])
                          ),
                      star_score,
                      sep=";", file=f)



if __name__ == "__main__":

    # Init lucene
    lucene.initVM()

    
    # Read command-line arguments
    import argparse
    parser = argparse.ArgumentParser(
        description='Execute queries on comment body')
    parser.add_argument('index_dir', metavar='dir', type=str,
                        help="Index directory")
    parser.add_argument('run_id', type=str,
                        help="AB_test run id")
    parser.add_argument('author', type=str, nargs='?',
                        default='', help="Author (for personalized results)")
    parser.add_argument('--sim', type=str, nargs='?',
                        default="tfidf", help="Similarity (in [tfidf, lm, bm25])")
    args = parser.parse_args()

    if args.sim in ['bm25']:
        similarity = BM25Similarity()
    elif args.sim in ['lm']:
        similarity = LMDirichletSimilarity()
    else:
        similarity = ClassicSimilarity()

    # Create 'results' directory
    if not os.path.isdir('results'):
        os.makedirs('results')

    # Start searcher
    storeDir = SimpleFSDirectory(Paths.get(args.index_dir))
    searcher = IndexSearcher(DirectoryReader.open(storeDir))
    if similarity is not None:
        searcher.setSimilarity(similarity)
    analyzer = StandardAnalyzer()
    run(searcher, analyzer, args.run_id)

