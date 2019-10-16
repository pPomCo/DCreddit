"""
Generate threads (using Neo4j/SQL)
and map textual data to each comment

Usage: import the DataGenerator class, use
 - get_textual_data to retrieve thread data using neo4j
 - get_textual_data to retrieve trad data in full SQL

Note: the smaller the day range, the faster the query
"""


import numpy as np
import time
from datetime import datetime




CYPHER_QUERY_THREAD = """
WITH
    %d AS date_min,
    %d AS date_max
MATCH
    path=(:Post)<-[:Parent]-(:Commentaire)<-[:Parent*..]-(cn:Commentaire)
WHERE
    date_min < cn.creation < date_max
WITH
    path, cn
UNWIND
    NODES(path)[1..] AS ci
WITH
    cn.nom AS id,
    COLLECT(ci.nom) AS thread
WITH
    id, thread, RAND() AS rnd
RETURN
    id,
    thread
ORDER BY
    rnd
"""


SQL_QUERY_TEXT = """
SELECT
    body,
    score,
    created_utc,
    subreddit
FROM
    May2015
WHERE
    name = ?
"""

SQL_QUERY_COMMENT = """
SELECT
    name
FROM
    May2015
WHERE
    created_utc > ?
    AND
    created_utc < ?
"""

SQL_QUERY_THREAD_TEXT = """
WITH RECURSIVE r(name, body, score, created_utc, subreddit, parent_id) AS (
    SELECT
        name,
        body,
        score,
        created_utc,
        subreddit,
        parent_id
    FROM
        May2015
    WHERE
        name = ?
    UNION
    SELECT
        May2015.name,
        May2015.body,
        May2015.score,
        May2015.created_utc,
        May2015.subreddit,
        May2015.parent_id
    FROM
        r,
        May2015
    WHERE
        r.parent_id = May2015.name
)
SELECT
    *
FROM
    r
"""
        




def batchify(iterable, batch_size):
    data = []
    for entry in iterable:
        data.append(entry)
        if len(data) == batch_size:
            yield data
            data = []
    return data






class DataGenerator(object):

    def __init__(self, graph, connection, day_range=(0,10000000000),
                 verbose=True):
        """Init with a neo4j connection and a sqlite connection"""
        self.graph = graph
        self.conn = connection
        self.day_range = day_range
        self.verbose = verbose



    def _fetch_cids(self):
        """Retrieve threads from Neo4j, yield lists of comment ids"""
        while True:
            if self.verbose:
                print("Querying Neo4j...")
            for record in self.graph.run(CYPHER_QUERY_THREAD%self.day_range):
                yield record['thread']

    def generate_textual_data(self):
        """Generate textual data related to threads using Neo4j/SQL"""
        c = self.conn.cursor()
        for thread in self._fetch_cids():
            yield [c.execute(SQL_QUERY_TEXT, (tid,)).fetchone()
                   for tid in thread]

    def generate_textual_data2(self):
        """Generate textual data related to threads using full SQLite"""
        c = self.conn.cursor()
        c2 = self.conn.cursor()
        while True:
            if self.verbose:
                print("Execute query")
            for comment in c.execute(SQL_QUERY_COMMENT, self.day_range):
                thread = list(c2.execute(SQL_QUERY_THREAD_TEXT, comment).fetchall())
                thread.reverse()
                yield thread
            

    def _fetch_ids(self):
        """Retrieve threads, yield records with comment, author, link and subreddit ids
        Using neo4j"""

        while True:
            if self.verbose:
                print("Querying Neo4j...")
            for record in self.graph.run(CYPHER_QUERY_THREAD_IDS%self.day_range):
                yield record


    def generate_thread_cids(self, batch_size=0):
        """Threads: lists of comment ids with the older one at first. """
        if batch_size <= 0:
            return self._fetch_cids()
        return batchify(self._fetch_cids(), batch_size)   


    def generate_thread_ids(self, batch_size=0):
        """Threads: lists of comment ids with the older one at first. """
        if batch_size <= 0:
            return self._fetch_ids()
        return batchify(self._fetch_ids(), batch_size)        








if __name__ == "__main__":

        
    from py2neo import Graph
    import sqlite3

    conn = sqlite3.connect('../../database.sqlite')
    graph = Graph(host='localhost', auth=('neo4j', 'May2015'))

    t = time.time()
    day_range = (datetime.timestamp(datetime(2015,5,10,12,0,0)),
                 datetime.timestamp(datetime(2015,5,11,12,0,0)))

    generator = DataGenerator(graph, conn, day_range=day_range)
    data = generator.generate_textual_data2()

    for i, item in enumerate(batchify(data, batch_size=1024)):
        print("%d\t%.3f\t%d\t%d\t%s"%(
            i,
            time.time()-t,
            len(item),
            max([len(t) for t in item]),
            str(item)[:80].replace('\n', ' ')
            ))
        t = time.time()
