

import sys, os, lucene, threading, time

from java.nio.file import Paths
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.index import \
    FieldInfo, IndexWriter, IndexWriterConfig, IndexOptions
from org.apache.lucene.store import SimpleFSDirectory




class Indexer(object):
    """Based on 'samples/IndexFiles.py'"""

    def __init__(self, storeDir):

        if not os.path.exists(storeDir):
            os.mkdir(storeDire)

        store = SimpleFSDirectory(Paths.get(storeDir))
        self.dir = store
        analyzer = StandardAnalyzer()
        config = IndexWriterConfig(analyzer)
        config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
        writer = IndexWriter(store, config)

        self.writer = writer


    def indexDocs(self, docs):
        """Index documents
        docs -- iterable over documents"""


        # Field types
        t1 = FieldType()
        t1.setStored(True)
        t1.setTokenized(False)
        t1.setIndexOptions(IndexOptions.DOCS_AND_FREQS)

        t2 = FieldType()
        t2.setStored(True)
        t2.setTokenized(True)
        t2.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)

        # Index each document
        for d in docs:
            doc = Document()
            doc.add(Field("name", d[0], t1))
            doc.add(Field("contents", d[1], t2))
            doc.add(Field("link_id", d[2], t1))
            self.writer.addDocument(doc)

        # Commit indexation
        self.writer.commit()
        self.writer.close()




if __name__ == "__main__":
    
    # Test indexing first 1000 rows
    DB_PATH = '../../database.sqlite'

    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    lucene.initVM()
    indexer = Indexer('index')


    sql_query = """SELECT name, body, link_id FROM May2015 LIMIT 100000"""
##    for row in c.execute(sql_query):
##        print(row)
    indexer.indexDocs(c.execute(sql_query))


    # Simple query on contents
    from org.apache.lucene.queryparser.classic import QueryParser
    from org.apache.lucene.index import DirectoryReader
    from org.apache.lucene.search import IndexSearcher
    query = QueryParser("contents", StandardAnalyzer()).parse("vitriol baltimore")
    searcher = IndexSearcher(DirectoryReader.open(indexer.dir))
    scoreDocs = searcher.search(query, 50).scoreDocs
    print(len(scoreDocs), "matching documents")
    for d in scoreDocs:
        print(d)
        print(searcher.doc(d.doc).getField('name'))
        print(searcher.doc(d.doc).getField('contents'))
        print(searcher.doc(d.doc).getField('link_id'))
    
    # Simple query on link_id
    query = QueryParser("link_id", StandardAnalyzer()).parse("t3_34f1bu")
    searcher = IndexSearcher(DirectoryReader.open(indexer.dir))
    scoreDocs = searcher.search(query, 50).scoreDocs
    print(len(scoreDocs), "matching documents")
    for d in scoreDocs:
        print(d)
        print(searcher.doc(d.doc).getField('name'))
        print(searcher.doc(d.doc).getField('contents'))
        print(searcher.doc(d.doc).getField('link_id'))
    
