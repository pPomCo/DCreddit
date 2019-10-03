# Database
DB = ../../data/sample10k.sqlite

# Similarities
MODELS = bm25 lm tf-idf

# Indexes directory
INDEXES = ../indexes

# Output directory
OUTDIR = out

# Sample queries
QUERIES = sample_queries.txt

# Programs
INDEXER = python3 ../indexer.py
SEARCHER = python3 ../searcher.py

test_all: $(foreach m, bm25 lm tf-idf, $(OUTDIR)/$(m).txt)


$(OUTDIR)/%.txt: $(QUERIES) $(INDEXES)/%/ | $(OUTDIR)
	cat $(QUERIES) | $(SEARCHER) $(INDEXES)/$* --sim $* > $@

$(INDEXES)/%/: $(INDEXES)
	$(INDEXER) $(DB) $@ --sim $*


$(OUTDIR) $(INDEXES):
	mkdir -p $@



clean:
	rm -fr $(OUTDIR)

maxclean: clean
	rm -fr $(INDEXES)


.PHONY: test_all clean maxclean
.PRECIOUS: $(OUTDIR)/%.txt $(INDEXES)/%/


