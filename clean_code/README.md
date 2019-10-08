# Clean code

Code that we are glad to share!

## Usage



### Indexation

1. Install *pylucene* (see [online instructions](http://lucene.apache.org/pylucene/install.html))
2. Check settings in the *Makefile*
3. Run *make*

It uses *lucene* to index the reddit comments database over the following fields:

- name
- author
- body
- link_id
- subreddit_id
- subreddit
- ups
- created_utc

The *body* field is stored (documents, frequencies, positions and term-vector) and lowercase-tokenized, so it enables to query by keywords and to access the document representation. All other fields are stored, and queries must match them exactly (case sensitive)

The representation model is BM25 (probabilistic model), which produces better performances than TF-IDF and LM when running our simple objective test (finding back comments from random words of their body)

	# Build index for the entire corpus
	make index

### Querying

We provide a very simple code to illustrate how to query comments on the previously build index

	# Start the interactive searcher
	make search


### Notes

 - To see how to call each python script, you can open the *Makefile* or run *python3 script.py -h*.
 - We use the BM25 to index so you HAVE TO use the BM25 to search into our index. If you rather use another similarity, you will have to build your own index with it.
