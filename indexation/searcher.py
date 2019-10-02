import sys, os, lucene, threading, time

from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.index import DirectoryReader





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
        scoreDocs = searcher.search(query, 50).scoreDocs
        print("%s total matching documents." % len(scoreDocs))

        for scoreDoc in scoreDocs:
            doc = searcher.doc(scoreDoc.doc)
            print(doc.get('name'), doc.get('body')[:100], '...')

        


if __name__ == "__main__":
    
    # Read command-line arguments
    import argparse
    parser = argparse.ArgumentParser(
        description='Execute queries on comment body')
    parser.add_argument('index_dir', metavar='dir', type=str,
                        help="Index directory")
    args = parser.parse_args()

    # Init lucene
    lucene.initVM()

    # Sample query
    storeDir = SimpleFSDirectory(Paths.get(args.index_dir))
    searcher = IndexSearcher(DirectoryReader.open(storeDir))
    analyzer = StandardAnalyzer()
    run(searcher, analyzer)
