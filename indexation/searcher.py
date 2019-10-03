import sys, os, lucene, threading, time

from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.search.similarities import \
     TFIDFSimilarity, LMDirichletSimilarity, BM25Similarity


N_DOCS = 10

def run(searcher, analyzer):
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


        # Reordering using ups
        scores = {}
        n_docs = len(scoreDocs)
        for i, scoreDoc in enumerate(scoreDocs):
            doc = searcher.doc(scoreDoc.doc)
            scores[scoreDoc.doc] = (n_docs-i, int(doc.get('ups')))
            ## TODO: normalize 'ups'
            ## (divide it by the maximum 'ups' of the subreddit)
            ## + weight scores

        print(scores)

        scoreDocs = sorted(scoreDocs, key=lambda sd: -sum(scores[sd.doc]))

        # Print results
        for i, scoreDoc in enumerate(scoreDocs):
            doc = searcher.doc(scoreDoc.doc)
            print()
            print("%d (sc=%d+%d=%d) (%s)"%(
                i,
                *scores[scoreDoc.doc], sum(scores[scoreDoc.doc]),
                doc.get('name')))
            print(doc.get('body'))

        


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
    args = parser.parse_args()


    if args.sim in ['bm25']:
        similarity = BM25Similarity()
    elif args.sim in ['lm']:
        similarity = LMDirichletSimilarity()
    else:
##        similarity = TFIDFSimilarity()
        similarity = None

    # Sample query
    storeDir = SimpleFSDirectory(Paths.get(args.index_dir))
    searcher = IndexSearcher(DirectoryReader.open(storeDir))
    if similarity is not None:
        searcher.setSimilarity(similarity)
    analyzer = StandardAnalyzer()
    run(searcher, analyzer)
