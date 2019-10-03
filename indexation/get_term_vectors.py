import sys, os, lucene, threading, time

from java.nio.file import Paths
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.index import DirectoryReader, IndexReader
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import BytesRef, BytesRefIterator




def main(storeDir):
    reader = DirectoryReader.open(storeDir)
    numDocs = reader.numDocs()
    print("n_docs:", numDocs)

    for i in range(numDocs):
        tvec = reader.getTermVector(i, 'body')
        if tvec is not None:
            termsEnum = tvec.iterator()
            vec = {}
            for term in BytesRefIterator.cast_(termsEnum):
                dpEnum = termsEnum.postings(None)
                dpEnum.nextDoc()
                vec[term.utf8ToString()] = dpEnum.freq()
            print(vec)
            
    reader.close()

if __name__ == "__main__":
    
    # Init lucene
    lucene.initVM()

    # Read command-line arguments
    import argparse
    parser = argparse.ArgumentParser(
        description='Build index on comments and users')
    parser.add_argument('index_dir', metavar='storeDir', type=str, nargs='?',
                        default='index/', help="path where to build index (default: 'index/')")
    args = parser.parse_args()

    storeDir = SimpleFSDirectory(Paths.get(args.index_dir))
    main(storeDir)
