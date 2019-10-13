"""
Execute query on comments

Querying can be automated by piping a query-file into this program. Each line
is a query, and an empty line (at least the last) stops the program.

Can set the representation model (TK-IDF, LM, BM25) depending on the index.
"""

import sys, os, lucene, threading, time

from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.search.similarities import \
     ClassicSimilarity, LMDirichletSimilarity, BM25Similarity


N_DOCS = 10

def run(searcher, analyzer, reordering='no', show_bodies=True):
    while True:
        # Read input line
        print()
        print("Hit enter with no input to quit.")
        command = input("Query:")
        if command == '':
            return

        # Execute query
        print()
        print("Searching for:", command)
        query = QueryParser("body", analyzer).parse(command)
        scoreDocs = searcher.search(query, N_DOCS).scoreDocs
        print("%s total matching documents." % len(scoreDocs))

        # Print results
        for i, scoreDoc in enumerate(scoreDocs):
            doc = searcher.doc(scoreDoc.doc)
            print("%d: %s [by %s]"%(i, doc.get('name'), doc.get('author') ))
            if show_bodies:
                print(doc.get('body'), "\n")

        


if __name__ == "__main__":

    # Init lucene
    lucene.initVM()

    
    # Read command-line arguments
    import argparse
    parser = argparse.ArgumentParser(
        description='Execute queries on comment body')
    parser.add_argument('index_dir', metavar='dir', type=str,
                        help="Index directory")
    parser.add_argument('--sim', type=str, nargs='?',
                        default="tfidf", help="Similarity (in [tfidf, lm, bm25])")
    parser.add_argument('--reorder', type=str, nargs='?',
                        default="no", help="Reordering (in [ups, normups])")
    parser.add_argument('--short', action='store_true',
                        help="Don't show the body of comments")
    args = parser.parse_args()

    if args.sim in ['bm25']:
        similarity = BM25Similarity()
    elif args.sim in ['lm']:
        similarity = LMDirichletSimilarity()
    else:
        similarity = ClassicSimilarity()


    # Start searcher
    storeDir = SimpleFSDirectory(Paths.get(args.index_dir))
    searcher = IndexSearcher(DirectoryReader.open(storeDir))
    if similarity is not None:
        searcher.setSimilarity(similarity)
    analyzer = StandardAnalyzer()
    run(searcher, analyzer, reordering=args.reorder, show_bodies=not args.short)
