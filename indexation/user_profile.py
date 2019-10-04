import sys, os, lucene, threading, time

from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.analysis.core import KeywordAnalyzer, WhitespaceAnalyzer
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.search.similarities import \
     ClassicSimilarity, LMDirichletSimilarity, BM25Similarity


N_DOCS = 100000

def user_profile(searcher, author):
    """Builds an user profile {comments, links, subreddits}"""

    analyzer = WhitespaceAnalyzer()
    query = QueryParser("author", analyzer).parse('"%s"'%author)
    scoreDocs = searcher.search(query, N_DOCS).scoreDocs

    profile = {'comments': set(), 'links': set(), 'subreddits': set()}
    for sd in scoreDocs:
        doc = searcher.doc(sd.doc)
        profile['comments'].add(doc.get('name'))
        profile['links'].add(doc.get('link_id'))
        profile['subreddits'].add(doc.get('subreddit'))

    return profile


if __name__ == "__main__":
    
    # Init lucene
    lucene.initVM()

    # Read command-line arguments
    import argparse
    parser = argparse.ArgumentParser(
        description='Build a user profile (sample)')
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
        similarity = ClassicSimilarity()



    # Instanciate searcher
    storeDir = SimpleFSDirectory(Paths.get(args.index_dir))
    searcher = IndexSearcher(DirectoryReader.open(storeDir))
    searcher.setSimilarity(similarity)


    # Open DB    
    import sqlite3
    conn = sqlite3.connect("../data/sample10k.sqlite")
    c = conn.cursor()

    # Build user profiles
    for row in c.execute("""SELECT DISTINCT author FROM May2015 LIMIT 100"""):
        user = row[0]
        if not "[" in user:
            print(user)
            profile = user_profile(searcher, analyzer, user)
            for k, v in profile.items():
                print("   ", k, v)
            
        
    c.close()
