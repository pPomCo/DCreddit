"""
Execute query on comments

Querying can be automated by piping a query-file into this program. Each line
is a query, and an empty line (at least the last) stops the program.

Can set the representation model (TK-IDF, LM, BM25) depending on the index.
"""

import sys, os, lucene, threading, time, pickle

from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.search.similarities import \
     ClassicSimilarity, LMDirichletSimilarity, BM25Similarity

import numpy as np
import pandas as pd
from numpy import linalg as LA
from cleantext import *

N_DOCS = 10

banned_users = "set(['', '[deleted]', 'AutoModerator', 'autowikibot', 'TweetsInCommentsBot', 'TweetPoster', 'TrollaBot', 'MTGCardFetcher', 'havoc_bot', 'TotesMessenger', 'TheNitromeFan', 'PoliticBot', 'autotldr', 'Late_Night_Grumbler', 'SharksPwn', 'WritingPromptsRobot', 'atomicimploder', 'Marvelvsdc00'])"
glove_path = "/projets/M2DC/team_JJJP/embeddings/glove.6B.200d.txt"
fusers_embeddings = "/projets/M2DC/team_JJJP/embeddings/userVec.csv"
ignored_users = eval(banned_users)
chunksize = 1*(10 ** 5)
testFile = "gtruth_link_25.csv"
user = "WyaOfWade"

def importEmbeddings(glove_path):
    '''
    Create matrix and index for wikipedia glove embeddings from glove_path file.
    Returns:
    - matrix_embeddings: vector for all words of glove dictionary
    - word2num: dictionary to identify row of a word
    - num2word: dictionary to identify word of a row
    '''
    maxwords = 400000
    dim = 200
    matrix_embeddings = np.zeros((maxwords,dim))
    word2num, num2word = dict(), dict()
    
    with open(glove_path, 'r') as f:
        for idx,line in enumerate(f):
            values = line.split()
            word2num[values[0]] = idx#word = values[0]
            num2word[idx] = values[0]
      
    embeddings_dict = {}
    with open(glove_path, 'r') as f:
        for idx,line in enumerate(f):
            values = line.split()
            word = values[0]
            vector = np.asarray(values[1:], "float32")
            matrix_embeddings[idx,:] = vector
    return matrix_embeddings, word2num, num2word


def getVectorEmb(list_words, model, word2num, num2word, dim=200):
    '''
    Calculate vector embedding : average term vector of comment
    '''
    doc = np.zeros(dim)
    tot = 0
    ids_list = []
    for word in list_words:
        idt = word2num.get(word,-1)
        if idt!= -1:
            ids_list.append(idt)
        
    tot = len(ids_list)
    if tot == 0:
        return doc.astype(np.float16)
    
    #print(ids_list)
    doc = np.sum(model[ids_list], axis=0)
    doc = doc/tot
    #print(doc)
    return doc.astype(np.float16)


def searchUserVec(username):
    res = []
    cols = [i for i in range(1,501)]
    for chunk in pd.read_csv(fusers_embeddings, chunksize=chunksize, sep='\t', header=None):
        
        tmp = chunk[0] == username
        df = chunk.loc[tmp]
        if len(df)!=0:
            res = df[cols]
            break
    return np.array(res)


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

def reorder_profile(scoreDocs, searcher, glove, word2num, num2word, centre_clusters, vuser, rusers, weights=(0.6,0.3,0.1)):
    """Reorder results using the personalised score 

    Return (ordered_scoreDocs, score_values)
    """
    scores = {}
    n_docs = len(scoreDocs)
    prefs = np.array([i for i in range(11,0,-1)])


    for i, scoreDoc in enumerate(scoreDocs):
        doc = searcher.doc(scoreDoc.doc)
        query_ups = QueryParser("subreddit", analyzer).parse(doc.get('subreddit'))

        text_comment = doc.get('body')
        user_comment = doc.get('author')


        # Get topics from comment
        listwords = clean_text(text_comment)
        docVec = getVectorEmb(listwords, glove, word2num, num2word)
        clusters = np.argsort(LA.norm(centre_clusters - docVec, axis=1))[:11]        
        vcomment = np.zeros(500)
        vcomment[clusters] += prefs

        scoreTopics = np.dot(vuser, vcomment) / ( LA.norm(vcomment)*LA.norm(vuser) )

        # Get social socre
        other_users = rusers.get(user_comment,None)
        scoreSocial = 0.0
        if other_users is not None:
            scoreSocial = rusers[user_comment] / max(list(rusers.values()))


        w_rank, w_theme, w_social = weights
        scores[scoreDoc.doc] = (w_rank * (n_docs-i)/n_docs,
                                w_theme * scoreTopics,
                                w_social * scoreSocial
                                )
    scoreDocs = sorted(scoreDocs, key=lambda sd: -sum(scores[sd.doc]))
    return scoreDocs, scores




def run(searcher, analyzer, ndocs=10, reordering='no', show_bodies=True):
    
    centre_clusters = np.load('scripts/cluster_centers.npy')
    with open('scripts/socialMatrix.pickle', 'rb') as handle:
        social_dict = pickle.load(handle)
    
    glove, word2num, num2word = importEmbeddings(glove_path)


    with open(testFile, newline='') as csvfile:
        tlines = csv.reader(csvfile, delimiter=';', quotechar='|')
        for line in tlines:
            #print()
            #print("Hit enter with no input to quit.")
            command = escape_lucene_special_chars(line[0])#input("Query:")
            if command == '':
                return

    ##        command = escape_lucene_special_chars(command)
            #print()
            #print("Searching for:", command)
            query = QueryParser("body", analyzer).parse(command)
            scoreDocs = searcher.search(query, ndocs).scoreDocs
            #print("%s total matching documents." % len(scoreDocs))


            if reordering == 'ups':
                scoreDocs, scores = reorder_ups(scoreDocs, searcher)
            elif reordering == 'normups':
                scoreDocs, scores = reorder_normups(scoreDocs, searcher)
            elif reordering =='profile':        
                vuser = searchUserVec(user)
                rusers = social_dict[user]
                scoreDocs, scores = reorder_profile(scoreDocs, searcher, glove, word2num, num2word, centre_clusters, vuser, rusers)

            else:
                n_docs = len(scoreDocs)
                scores = {sd.doc: (n_docs-i,) for i,sd in enumerate(scoreDocs)}

            # Print results
            topres = []
            for i, scoreDoc in enumerate(scoreDocs):
                doc = searcher.doc(scoreDoc.doc)
                topres.append(doc.get('name'))
                
                
                # print("%d: %s [by %s] (score: %s)"%(
                #     i,
                #     doc.get('name'),
                #     doc.get('author'),
                #     "%s=%.3f"%(
                #         "+".join(["%.3f"%x for x in scores[scoreDoc.doc]]),
                #         sum(scores[scoreDoc.doc])
                #         )
                #     ))
                # if not show_bodies:
                #     print(doc.get('body'), "\n")
            print(",".join(topres))
        


if __name__ == "__main__":

    # Init lucene
    lucene.initVM()

    
    # Read command-line arguments
    import argparse
    parser = argparse.ArgumentParser(
        description='Execute personalised queries on comment body')
    parser.add_argument('index_dir', metavar='dir', type=str,
                        help="Index directory")
    parser.add_argument('--ndocs', type=int, nargs='?',
                        default=N_DOCS, help="Number of documents to return for each query")
    parser.add_argument('--sim', type=str, nargs='?',
                        default="tfidf", help="Similarity (in [tfidf, lm, bm25])")
    parser.add_argument('--reorder', type=str, nargs='?',
                        default="profile", help="Reordering (in [ups, normups, profile])")
    parser.add_argument('--user', type=str, nargs='?',
                        default="WyaOfWade", help="User to pick from database")
    parser.add_argument('--testFile', type=str, nargs='?',
                        default="gtruth_link_25.csv", help="Path of qrel file")
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
    run(searcher, analyzer, ndocs=args.ndocs, reordering=args.reorder, show_bodies=not args.short)
