# Database
DB = ../../data/sample10k.sqlite

# Similarities
MODELS = bm25 lm tfxidf

# Reordering
REORDER = no ups normups

# Indexes directory
INDEXES = ../indexes

# Output directory
OUTDIR = out

# Sample queries
QUERIES = sample_queries.txt

# Programs
INDEXER = python3 ../indexer.py
SEARCHER = python3 ../searcher.py

test_all: $(foreach ord, $(REORDER), $(foreach m, $(MODELS), $(OUTDIR)/$(m)-$(ord).txt))


$(OUTDIR)/%-no.txt: $(QUERIES) $(INDEXES)/%/ | $(OUTDIR)
	cat $(QUERIES) | $(SEARCHER) $(INDEXES)/$* --sim $* --short > $@
$(OUTDIR)/%-ups.txt: $(QUERIES) $(INDEXES)/%/ | $(OUTDIR)
	cat $(QUERIES) | $(SEARCHER) $(INDEXES)/$* --sim $* --reorder ups --short > $@
$(OUTDIR)/%-normups.txt: $(QUERIES) $(INDEXES)/%/ | $(OUTDIR)
	cat $(QUERIES) | $(SEARCHER) $(INDEXES)/$* --sim $* --reorder normups --short > $@

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


