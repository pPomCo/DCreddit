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


def reorder_ups(scoreDocs, searcher):
    """Reorder results using the score 'n_docs - rank + ups'

    Return (ordered_scoreDocs, score_values)"""
    scores = {}
    n_docs = len(scoreDocs)
    for i, scoreDoc in enumerate(scoreDocs):
        doc = searcher.doc(scoreDoc.doc)
        scores[scoreDoc.doc] = (n_docs-i, int(doc.get('ups')))
    scoreDocs = sorted(scoreDocs, key=lambda sd: -sum(scores[sd.doc]))
    return scoreDocs, scores

def reorder_normups(scoreDocs, searcher, weights=(0.8,0.2)):
    """Reorder results using the score w[0]*sc_rank + w[1]*sc_ups
       where sc_rank = (n_docs-rank)/n_docs
             sc_ups = ups / max(abs(ups_of_subreddit))

    Return (ordered_scoreDocs, score_values)
    """
    scores = {}
    n_docs = len(scoreDocs)
    for i, scoreDoc in enumerate(scoreDocs):
        doc = searcher.doc(scoreDoc.doc)
        query_ups = QueryParser("subreddit", analyzer).parse(doc.get('subreddit'))
        scoreDocs_ups = searcher.search(query_ups, 1000).scoreDocs
        max_ups = 0
        for sd_ups in scoreDocs_ups:
            max_ups = max(max_ups, abs(int(searcher.doc(sd_ups.doc).get('ups'))))
        if max_ups == 0:
            max_ups = 1

        w_rank, w_ups = 0.7, 0.3
        scores[scoreDoc.doc] = (w_rank * (n_docs-i)/n_docs,
                                w_ups * int(doc.get('ups'))/max_ups)
    scoreDocs = sorted(scoreDocs, key=lambda sd: -sum(scores[sd.doc]))
    return scoreDocs, scores






def run(searcher, analyzer, reordering='no', show_bodies=True):
    while True:
        print()
        print("Hit enter with no input to quit.")
        command = input("Query:")
        if command == '':
            return

        print()
        print("Searching for:", command)
        query = QueryParser("body", analyzer).parse(command)
        scoreDocs = searcher.search(query, N_DOCS).scoreDocs
        print("%s total matching documents." % len(scoreDocs))


        if reordering == 'ups':
            scoreDocs, scores = reorder_ups(scoreDocs, searcher)
        elif reordering == 'normups':
            scoreDocs, scores = reorder_normups(scoreDocs, searcher)
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
    run(searcher, analyzer, reordering=args.reorder, show_bodies=not args.short)
