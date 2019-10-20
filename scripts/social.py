import sys, argparse
import pickle
from collections import Counter
import sqlite3, math, csv, re, gc
import pandas as pd
import datetime
from array import array

import numpy as np
from numpy import linalg as LA

#%matplotlib inline
#%matplotlib qt
from cleantext import *


banned_users = "set(['', '[deleted]', 'AutoModerator', 'autowikibot', 'TweetsInCommentsBot', 'TweetPoster', 'TrollaBot', 'MTGCardFetcher', 'havoc_bot', 'TotesMessenger', 'TheNitromeFan', 'PoliticBot', 'autotldr', 'Late_Night_Grumbler', 'SharksPwn', 'WritingPromptsRobot', 'atomicimploder', 'Marvelvsdc00'])"
default_path_db= "/projets/M2DC/data/database.sqlite"


def connectDB(db=default_path_db):
    '''
    Connect to db file.
    Returns: Cursor
    '''
    conn = sqlite3.connect(db)
    return conn.cursor()


def previewDict(mydict):
    '''
    Print first 10 key,values of a dictionary
    '''
    count = 0
    for key, val in mydict.items():
        print(key, val)
        count+=1
        if count>10:
            break

def prepareUserMatrix():
    '''
    Save a matrix with all the interactions between users from the database
    '''

    print("Connecting db...",flush=True)
    db = connectDB()

    parents, author = dict(), dict()

    query = "SELECT name, author, parent_id FROM May2015"
    lines = db.execute(query)
    ignored_users = eval(banned_users)

    print("Making list of comments and parents")
    # prepare dicts to faster search
    for line in lines:
        #print(line[0], line[2])
        idc = line[0]# comment id
        idp = line[2] # comment parent id
        user = line[1] #user
        if user in ignored_users:
            continue
        parents[idc] = idp
        author[idc] = user

    previewDict(parents)
    previewDict(author)
    # construct social matrix
    print("Making social matrix")
    social = dict()
    for comment,parent_comment in parents.items():
        author_comment = author[comment]

        #check if parent comment exists in bd
        parent_id = author.get(parent_comment, None)
        if parent_id is None:
            continue

        # Gets interaction diciionary from a user, if it does not exist we create one
        interact_user = social.get(author_comment, None)
        if interact_user is None:
            interact_user = dict()
        # adds interaction
        parent_author = author[parent_comment]
        interact_user[parent_author] = interact_user.get(parent_author,0) + 1
        social[author_comment] = interact_user

    print("Normalizing matrix...")
    # normalize social matrix
    for user, interactions in social.items():
        total = sum(interactions.values())
        n_interactions = dict()
        for nuser, freq in interactions.items():
            n_interactions[nuser] = 1.0*freq/total
        social[user] = n_interactions

    # save
    print("Saving dictionary")
    with open('socialMatrix.pickle', 'wb') as handle:
        pickle.dump(social, handle, protocol=pickle.HIGHEST_PROTOCOL)
    

def recommendToUser():
    '''
    Search new users to recommend based on the previous interactions
    '''
    print("Load dictionary")
    with open('socialMatrix.pickle', 'rb') as handle:
        social=pickle.load(handle)

    print("Creating matrix recommendation for ", len(social.keys()), " users")
    topU = 11
    recomMatrix = dict()
    for idx,(user,interactions) in enumerate(social.items()):

        totalU = dict()
        
        tot = min(len(list(interactions.keys())),topU)
        top_users = sorted(interactions.items(), key=lambda kv: kv[1], reverse=True)[:tot] #use only top users

        for user2,freq in top_users:
            #walks through the vector of user2
            sndlvlU = social.get(user2,None)
            if sndlvlU is None:
                tot-=1
                continue

            tot2 = min(len(list(interactions.keys())),topU)
            top_users2 = sorted(sndlvlU.items(), key=lambda kv: kv[1], reverse=True)[:tot2] #use only top users
            for user3, freq2 in top_users2:
                totalU[user3] = totalU.get(user3,0)+freq # update weigth

        finalRec = dict()
        for user2,freq in totalU.items():
            finalRec[user2] = freq/tot*1.0
        #previewDict(finalRec)

        tot3 = min(len(list(finalRec.keys())),topU)
        sorted_users = sorted(finalRec.items(), key=lambda kv: kv[1], reverse=True)[:min(tot3,topU)]
        myUsers = set(interactions.keys())
        toRecommend = []
        for user2,freq in sorted_users:
            if user2 in myUsers:
                continue
            toRecommend.append((user2,freq))
        recomMatrix[user] = toRecommend
        if idx%50000 == 0:
            print(idx,"Users")
            gc.collect()


    # save
    print("Saving dictionary")
    with open('recMatrix.pickle', 'wb') as handle:
        pickle.dump(recomMatrix, handle, protocol=pickle.HIGHEST_PROTOCOL)


def main(argv):    
    if args.matrix:
        prepareUserMatrix()
    if args.recomm:
        recommendToUser()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Create social vector user profiles from database.\nPaths for resources at top of the code.')

    parser.add_argument('-db', dest='db', help="Database path to read users and comments.")
    parser.add_argument('-m',  '--matrix', action='store_true', help="Compute the social matrix (response ratio) between users.")
    parser.add_argument('-r',  '--recomm', action='store_true', help="Returns a list of recommended user to follow for each user.")
    args = parser.parse_args()
    main(args)
