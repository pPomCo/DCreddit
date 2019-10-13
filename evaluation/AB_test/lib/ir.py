import sys, os, lucene, threading, time

from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.search.similarities import \
     ClassicSimilarity, LMDirichletSimilarity, BM25Similarity

INDEXDIR = '../../indexation/indexes/bm25'


# Init lucene

print("Init lucene...", end=" ", flush=True)
lucene.initVM()
similarity = BM25Similarity()
storeDir = SimpleFSDirectory(Paths.get(INDEXDIR))
searcher = IndexSearcher(DirectoryReader.open(storeDir))
searcher.setSimilarity(similarity)
analyzer = StandardAnalyzer()
print("done")


def escape_lucene_special_chars(string):
    for c in ['\\', '+', '-', '&&', '||', '!', '(', ')', '{', '}', '[', ']',
              '^', '"', '~', '*', '?', ':', '/']:
        string = string.replace(c, ' ')
    return string


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


def reorder_long(scoreDocs, searcher, weights=(0.7, 0.3)):
    """Reorder results using the score w[0]*sc_rank + w[1]*sc_len
       where sc_rank = (n_docs-rank)/n_docs
             sc_len = len/max_len

    Return (ordered_scoreDocs, score_values)"""
    scores = {}
    n_docs = len(scoreDocs)
    for i, scoreDoc in enumerate(scoreDocs):
        doc = searcher.doc(scoreDoc.doc)
        scores[scoreDoc.doc] = ((n_docs-i)/n_docs, len(doc.get('body')))
    max_len = max([v for k,(u,v) in scores.items()])
    scores = {k: (weights[0]*u, weights[1]*v/max_len)
              for k,(u,v) in scores.items()}
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

        scores[scoreDoc.doc] = (weights[0] * (n_docs-i)/n_docs,
                                weights[1] * int(doc.get('ups'))/max_ups)
    scoreDocs = sorted(scoreDocs, key=lambda sd: -sum(scores[sd.doc]))
    return scoreDocs, scores






def search(command):

    reordering = 'no'

    vm_env = lucene.getVMEnv()
    vm_env.attachCurrentThread()

    command = escape_lucene_special_chars(command)
    print("Searching for:", command)
    query = QueryParser("body", analyzer).parse(command)
    scoreDocs = searcher.search(query, 100).scoreDocs


    if reordering == 'ups':
        scoreDocs, scores = reorder_ups(scoreDocs, searcher)
    elif reordering == 'long':
        scoreDocs, scores = reorder_long(scoreDocs, searcher)
    elif reordering == 'normups':
        scoreDocs, scores = reorder_normups(scoreDocs, searcher)
    else:
        n_docs = len(scoreDocs)
        scores = {sd.doc: (n_docs-i,) for i,sd in enumerate(scoreDocs)}

    scoreDocs = scoreDocs[:5]

    for sd in scoreDocs:
        print(sd.doc,'\t',scores[sd.doc])

    docs = [searcher.doc(sd.doc) for sd in scoreDocs]
    return [(d.get('name'), d.get('body')) for d in docs]

        
