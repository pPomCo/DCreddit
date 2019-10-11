
import sys, os, lucene, threading, time
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.analysis.core import WhitespaceAnalyzer




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
    analyzer = WhitespaceAnalyzer()
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

def reorder_null(scoreDocs, searcher):
    n_docs = len(scoreDocs)
    scores = {sd.doc: (n_docs-i,) for i,sd in enumerate(scoreDocs)}
    return scoreDocs, scores
