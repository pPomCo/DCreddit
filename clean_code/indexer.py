"""
Index comments from a sqlite3 db.

Can use TF-IDF, language model and BM25.

Indexed fields are :
        'name': t1,
        'author': t1,
        'body': t2,
        'ups': t3,
        'link_id': t1
        'subreddit': t1,
        'subreddit_id': t1,

Where the FieldTypes are :
        t1: store (docss freqs)
        t2: tokenize (docs, freqs, positions, term vectors)
        t3: store (docs)

"""
import sys, os, lucene, threading, time

from java.nio.file import Paths
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.index import \
    FieldInfo, IndexWriter, IndexWriterConfig, IndexOptions
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.search.similarities import \
     ClassicSimilarity, LMDirichletSimilarity, BM25Similarity


class Indexer(object):
    """Index a collection

    Based on 'samples/IndexFiles.py'"""

    def __init__(self, storeDir, similarity=None):
        """Constructor

        storeDir -- path where to save the index
        similarity (opt) -- similarity"""

        if not os.path.exists(storeDir):
            os.mkdir(storeDir)

        store = SimpleFSDirectory(Paths.get(storeDir))
        self.dir = store
        analyzer = StandardAnalyzer()
        config = IndexWriterConfig(analyzer)
        config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
        if similarity is not None:
            config.setSimilarity(similarity)
        writer = IndexWriter(store, config)

        self.writer = writer


    def indexDocs(self, fields, docs):
        """Index documents

        fields -- {name: FieldType} for each indexed field
        docs -- iterable over documents"""

        # Index each document
        t = time.time()
        for i, d in enumerate(docs):
            if i % 100000 == 0:
                print("Indexing doc #%d (time: %.2f)"%(i, time.time()-t))
                t = time.time()
            doc = Document()
            for i, (field_name, field_type) in enumerate(fields.items()):
                doc.add(Field(field_name, d[i], field_type))
            self.writer.addDocument(doc)

        # Commit indexation
        self.writer.commit()
        self.writer.close()




if __name__ == "__main__":

    # Init lucene
    lucene.initVM()

    # Read command-line arguments
    import argparse
    parser = argparse.ArgumentParser(
        description='Build index on comments and users')
    parser.add_argument('db', metavar='DB', type=str,
                        help="path of the sqlite3 database to index")
    parser.add_argument('storeDir', metavar='storeDir', type=str, nargs='?',
                        default='index/', help="path where to build index (default: 'index/')")
    parser.add_argument('rel_name', metavar='relation', type=str, nargs='?',
                        default="May2015", help="Relation name (default: 'May2015')")
    parser.add_argument('--sim', type=str, nargs='?',
                        default="tfidf", help="Similarity (in [tfidf, lm, bm25])")
    args = parser.parse_args()


    if args.sim in ['bm25']:
        similarity = BM25Similarity()
    elif args.sim in ['lm']:
        similarity = LMDirichletSimilarity()
    else:
        similarity = ClassicSimilarity()


    # Open DB    
    import sqlite3
    conn = sqlite3.connect(args.db)
    c = conn.cursor()


    # Field types
    t1 = FieldType()
    t1.setStored(True)
    t1.setTokenized(False)
    t1.setIndexOptions(IndexOptions.DOCS_AND_FREQS)

    t2 = FieldType()
    t2.setStored(True)
    t2.setTokenized(True)
    t2.setStoreTermVectors(True)
    t2.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)

    t3 = FieldType()
    t3.setStored(True)
    t3.setTokenized(False)
    t3.setIndexOptions(IndexOptions.DOCS)

    
    # Fields to index (comments)
    fields = {
        'name': t1,
        'author': t1,
        'body': t2,
        'ups': t3,
        'link_id': t1,
        'subreddit': t1,
        'subreddit_id': t1,
        }



    # Indexation
    indexer = Indexer(storeDir=args.storeDir, similarity=similarity)

    field_names = ", ".join(fields.keys())
    sql_query = """SELECT %s FROM %s"""%(field_names, args.rel_name)

    indexer.indexDocs(fields, c.execute(sql_query))


