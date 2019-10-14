import sys, argparse
from collections import Counter
import sqlite3, math, csv, re
import pandas as pd
import datetime
from array import array

import numpy as np
from numpy import linalg as LA

#%matplotlib inline
#%matplotlib qt
from sklearn.model_selection import train_test_split
from sklearn.metrics import auc, accuracy_score, confusion_matrix, mean_absolute_error
from sklearn.metrics.pairwise import euclidean_distances
from sklearn import preprocessing
from sklearn.cluster import MiniBatchKMeans, KMeans
from gensim.models import Word2Vec, KeyedVectors
from gensim.test.utils import datapath, get_tmpfile
from gensim.scripts.glove2word2vec import glove2word2vec

from cleantext import *


banned_users = "set(['', '[deleted]', 'AutoModerator', 'autowikibot', 'TweetsInCommentsBot', 'TweetPoster', 'TrollaBot', 'MTGCardFetcher', 'havoc_bot', 'TotesMessenger', 'TheNitromeFan', 'PoliticBot', 'autotldr', 'Late_Night_Grumbler', 'SharksPwn', 'WritingPromptsRobot', 'atomicimploder', 'Marvelvsdc00'])"

default_path_db= "/projets/M2DC/data/database.sqlite"
glove_path = "/projets/M2DC/team_JJJP/embeddings/glove.6B.200d.txt"
comments_embeddings = "/projets/M2DC/team_JJJP/embeddings/textVec.csv"
fusers_embeddings = "/projets/M2DC/team_JJJP/embeddings/userVec.csv"
chunksize = 1*(10 ** 5)

def connectDB(db=default_path_db):
    '''
    Connect to db file.
    Returns: Cursor
    '''
    conn = sqlite3.connect(db)
    return conn.cursor()


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



def getCleanedComments(conn):
    '''
    Returns the comment id, author, subreddit id and list of valid words for
    each comment in the database
    '''
    ignored_users = eval(banned_users)
    query = "SELECT id, author, subreddit_id, body from May2015"
    for line in conn.execute(query):
        comment_id = line[0]
        author = line[1]
        subreddit_id = line[2]
        text = line[3]
        
        # if it is a banned user we skip
        if author in ignored_users:
            continue
        
        listwords = clean_text(text)
        # empty string
        if len(listwords)==0:
            continue
        
        yield comment_id, author, subreddit_id, listwords

    
def getCleanedCommentsInBatch(lines):
    '''
    Same as getCleanedComments but in batchs
    '''
    ignored_users = eval(banned_users)
    for line in lines:
        comment_id = line[0]
        author = line[1]
        subreddit_id = line[2]
        text = line[3]
        
        # if it is a banned user we skip
        if author in ignored_users:
            continue
        
        listwords = clean_text(text)
        # empty string
        if len(listwords)==0:
            continue        
        yield comment_id, author, subreddit_id, listwords


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


def prepareEmbeddingSet():
    '''
    Create a file with all embeddings (200d) for each comment in the dataset
    Returns: Write a CSV file with all the vector for the database comments
    '''
    print("Connecting db...",flush=True)
    db = connectDB()
    print("Loading Glove embeddings...",flush=True)
    glove, word2num, num2word = importEmbeddings(glove_path)
    en = 0
    print("Cleaning text files...",flush=True)
    with open(fcomments_embeddings, mode='w') as f:
        writer = csv.writer(f, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for comment_id, author, subreddit_id, listwords in getCleanedComments(db):
            
            docVec = getVectorEmb(listwords, glove, word2num, num2word)
            tline = np.append(np.array([comment_id, author, subreddit_id]),docVec)
            #(tline)
            #print(tline.shape)
            writer.writerow(tline)
            en+=1
            if en%100000==0:
                print(en)
    

def getAllSubReddits():
    '''
    Returns  all subreddits and a dictionary of id_comment -> id_subreddit
    '''
    c = connectDB()
    subrd = set()
    mapSubs = dict()
    lines = c.execute("SELECT id, subreddit_id FROM May2015")
    for line in lines:
        subrd.add(line[1])
        mapSubs[line[0]] = line[1]
    return subrd, mapSubs


def processComments(chunk, com2sub, le, matrix, count_matrix):
    '''
    Update matrix and count_matrix with the embedded vector and frequency
    respectively.
    Returns: matrix and count_matrix updated
    '''
    df = chunk#pd.DataFrame(chunk)
    #print(df.head())
    cols = [i for i in range(3,203)]  # col names for df
    comm = df[0] # comment id
    comments_sub_names = comm.apply(lambda x: com2sub[x])
    sub_ids = le.transform(comments_sub_names)
    
    np.add.at(matrix,sub_ids,df[cols].astype(np.single))
    np.add.at(count_matrix,sub_ids, 1)
    #print(matrix, np.sum(count_matrix))
    return matrix, count_matrix


def findUserComment(row, centre_clusters, prefs):
    vcols = [str(i) for i in range(200)]
    #print(row[vcols])
    comment = np.array(row[3:203], dtype=np.double) # embedding
    clusters = np.argsort(LA.norm(centre_clusters - comment, axis=1))[:11]

    vuser = np.zeros(500)
    vuser[clusters] += prefs
    user = np.array([row[1]]) # id author
    return np.append(user, vuser)

def processUserComments(df, centre_clusters, uProf, topK=11):
    '''
    Find nearest topics for a comment user
    '''
    vcols = [str(i) for i in range(200)]

    users = df['user']
    ndf = df[vcols] # comments vectors
#     dist_topics = np.zeros((ndf.shape[0], centre_clusters.shape[0] ))
#     for topic in range(centre_clusters.shape[0]):
#         print(topic)
#         dist_topics[:,topic] = LA.norm(ndf-centre_clusters[topic,:], axis=1)
    dist_topics = euclidean_distances(ndf, centre_clusters)
    best_index = np.argsort(dist_topics, axis=1)[:,:topK]
   
    #print("Updating user vector...")
    prefs = np.array([i for i in range(1,12)])
    for user,best_topics in zip(users, best_index):
        vuser = uProf.get(user, np.zeros(500))
        vuser[best_topics] += prefs
        uProf[user] = vuser
    
    return uProf


def prepareUserEmbeddings():
    '''
    Write userVec file with the embedding profile for all users
    '''
    print("Reading clusters...",flush=True)
    vecUsers = dict()
    centre_clusters = np.load('cluster_centers.npy')

    #load emb vectors
    print("Calculating users average...",flush=True)
    filename = fcomments_embeddings
    vcols = [str(i) for i in range(200)]
    cols = np.append(np.array(['id','user','subr']), vcols)
    
    for chunk in pd.read_csv(filename, chunksize=chunksize ,sep='\t', header=None, names=cols):
        #print("Batch")
        vecUsers = processUserComments(chunk, centre_clusters, vecUsers)
    
    print("Normalizing vectors...",flush=True)
    #normalize vector
    with open(fusers_embeddings, mode='w') as f:
        writer = csv.writer(f, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for key,val in vecUsers.items():
            vectorU = val/val.max()
            line = np.append( np.array([key]),vectorU.astype(np.float16))
            writer.writerow(line)


def prepareUserEmbeddingsOnline():
    '''
    Write userVec file with the embedding profile for all users
    '''
    print("Connecting db...",flush=True)
    db = connectDB()
    print("Loading Glove embeddings...",flush=True)
    glove, word2num, num2word = importEmbeddings(glove_path)
    
    vecUsers = dict()
    centre_clusters = np.load('cluster_centers.npy')

    #load emb vectors
    vcols = [str(i) for i in range(200)]
    cols = np.append(np.array(['id','user','subr']), vcols)
    print("Cleaning text files...",flush=True)
    query = "SELECT id, author, subreddit_id, body FROM May2015 WHERE created_utc<1432512000"
    results = db.execute(query)
    count = 0
    batch, dfbatch = [], []
    for line in results:
    	if count <chunksize:
	    	batch.append(line)
			count = count +1
            continue
        batch.append(line)
        dfbatch = []
		for comment_id, author, subreddit_id, listwords in getCleanedCommentsInBatch(batch):
            docVec = getVectorEmb(listwords, glove, word2num, num2word)
            tline = np.append(np.array([comment_id, author, subreddit_id]),docVec)
            dfbatch.append(tline)
        
        print("Processing batch",flush=True)
        chunk = pd.DataFrame(dfbatch, columns = cols) 
        vecUsers = processUserComments(chunk, centre_clusters, vecUsers)
            
    # Remaining ones
    dfbatch = []
    for comment_id, author, subreddit_id, listwords in getCleanedCommentsInBatch(batch):
        docVec = getVectorEmb(listwords, glove, word2num, num2word)
        tline = np.append(np.array([comment_id, author, subreddit_id]),docVec)
        dfbatch.append(tline)    
    print("Processing batch",flush=True)
    chunk = pd.DataFrame(dfbatch, columns = cols) 
    vecUsers = processUserComments(chunk, centre_clusters, vecUsers)


    print("Normalizing vectors...",flush=True)
    #normalize vector
    with open(fusers_embeddings, mode='w') as f:
        writer = csv.writer(f, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for key,val in vecUsers.items():
            vectorU = val/val.max()
            line = np.append( np.array([key]),vectorU.astype(np.float16))
            writer.writerow(line)


def subreddit2vector():
    '''
    Return embedded vector for all subreddit in dataset
    Returns: Save subreddit_matrix and cluster_centers variables
    '''

    print("Preparing subreddits info...",flush=True)
    le = preprocessing.LabelEncoder()
    allsubs, com2sub = getAllSubReddits() # get all Subreddits
    le.fit(list(allsubs))
    subdict = dict() # id_sub -> vector

    print("Getting comments vector",flush=True)
    # store accum vector for each subreddit
    totsubs = len(allsubs) # total subreddits
    sreddit_matrix = np.zeros((totsubs,200))
    count_sreddit_matrix = np.zeros(totsubs)

    #load emb vectors
    print("Calculating subreddits average...",flush=True)
    filename = fcomments_embeddings
    for chunk in pd.read_csv(filename, chunksize=chunksize ,sep='\t', header=None):
        sreddit_matrix, count_sreddit_matrix = \
            processComments(chunk, com2sub, le, sreddit_matrix, count_sreddit_matrix)

    print("Finishin subreddit vectors...",flush=True)
    # Get average of comments in subreddit
    avg_matrix = np.divide(sreddit_matrix, count_sreddit_matrix[:,None], where=count_sreddit_matrix[:,None]!=0)
    # Save it!
    np.save('subreddit_matrix',avg_matrix)

    #bsize = (10**5)
    # Find cluster centers
    #kmeans = MiniBatchKMeans(n_clusters=500, random_state=42, batch_size=bsize)
    kmeans = KMeans(n_clusters=500, random_state=42)
    kmeans = kmeans.fit(avg_matrix)

    np.save('cluster_centers',kmeans.cluster_centers_)

    
def subreddit2vectorOnline():
    '''
    Return embedded vector for all subreddit in dataset from Scratch
    Returns: Save subreddit_matrix and cluster_centers variables
    '''

    print("Connecting db...",flush=True)
    db = connectDB()
    print("Loading Glove embeddings...",flush=True)
    glove, word2num, num2word = importEmbeddings(glove_path)
    
    print("Preparing subreddits info...",flush=True)
    le = preprocessing.LabelEncoder()
    allsubs, com2sub = getAllSubReddits() # get all Subreddits
    le.fit(list(allsubs))
    subdict = dict() # id_sub -> vector

    print("Getting comments vector",flush=True)
    # store accum vector for each subreddit
    totsubs = len(allsubs) # total subreddits
    sreddit_matrix = np.zeros((totsubs,200))
    count_sreddit_matrix = np.zeros(totsubs)

    #load emb vectors
    print("Cleaning text files...",flush=True)
    query = "SELECT id, author, subreddit_id, body FROM May2015 WHERE created_utc<1432512000"
    results = db.execute(query)

    count = 0
    batch, dfbatch = [], []
    for line in results:
        if count <chunksize:
	    	batch.append(line)
            count = count +1
            continue
        batch.append(line)
        dfbatch = []
		for comment_id, author, subreddit_id, listwords in getCleanedCommentsInBatch(batch):
            docVec = getVectorEmb(listwords, glove, word2num, num2word)
            tline = np.append(np.array([comment_id, author, subreddit_id]),docVec)
        	dfbatch.append(tline)
    	print("Processing batch",flush=True)
		chunk = pd.DataFrame(dfbatch)   
		sreddit_matrix, count_sreddit_matrix = \
             processComments(chunk, com2sub, le, sreddit_matrix, count_sreddit_matrix)

    # Remaining ones        
    dfbatch = []
    for comment_id, author, subreddit_id, listwords in getCleanedCommentsInBatch(batch):
        docVec = getVectorEmb(listwords, glove, word2num, num2word)
        tline = np.append(np.array([comment_id, author, subreddit_id]),docVec)
        dfbatch.append(tline)
    print("Processing batch",flush=True)
    chunk = pd.DataFrame(dfbatch)   
    sreddit_matrix, count_sreddit_matrix = \
        processComments(chunk, com2sub, le, sreddit_matrix, count_sreddit_matrix)


    print("Ending subreddit vectors...",flush=True)
    # Get average of comments in subreddit
    avg_matrix = np.divide(sreddit_matrix, count_sreddit_matrix[:,None], where=count_sreddit_matrix[:,None]!=0)
    # Save it!
    np.save('subreddit_matrix',avg_matrix)

    #bsize = (10**5)
    # Find cluster centers
    #kmeans = MiniBatchKMeans(n_clusters=500, random_state=42, batch_size=bsize)
    kmeans = KMeans(n_clusters=500, random_state=42)
    kmeans = kmeans.fit(avg_matrix)
    np.save('cluster_centers',kmeans.cluster_centers_)
    
    
    
def main(argv):    
    if args.comments:
        #prepareEmbeddingSet(args.db)
        prepareEmbeddingSet()
    if args.subreddits:
        #subreddit2vector()
        subreddit2vectorOnline()
    if args.users:
        #prepareUserEmbeddings()
        prepareUserEmbeddingsOnline()
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-db', dest='db')
    parser.add_argument('-c',  '--comments', action='store_true')
    parser.add_argument('-s',  '--subreddits', action='store_true')
    parser.add_argument('-u',  '--users', action='store_true')
    args = parser.parse_args()
    main(args)
