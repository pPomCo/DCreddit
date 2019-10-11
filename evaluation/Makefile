# Searcher
NDOCS = 25
SIMILARITY = bm25
REORDERING = no
SEARCHER_EXE = ../indexation/searcher.py
SEARCHER = python3 $(SEARCHER_EXE) ../indexation/indexes/$(SIMILARITY) --sim $(SIMILARITY) --short --ndocs $(NDOCS) --reorder $(REORDERING)

# Evaluation
TREC = trec_eval.8.1/trec_eval

# Test set
TESTDIR = tests/$(SIMILARITY)/$(REORDERING)
SRC_COMM = syseval/scores/out/5/gtruth.csv
GT_COMM = $(TESTDIR)/comm_qrels.test
RE_COMM = $(TESTDIR)/comm_results.test
SC_COMM = $(TESTDIR)/comm_out.test
NQ_LINK = 1000
SRC_LINK = wrapper_reddit/links/gtruth_link_$(NQ_LINK).csv
GT_LINK = $(TESTDIR)/links_qrels.test
RE_LINK = $(TESTDIR)/links_results.test
SC_LINK = $(TESTDIR)/links_out.test

# Utils
FORMAT_QUERY = python3 lib/format_query.py

test: $(TREC) link_test comm_test

$(TREC):
	+make -C $(dir $@) $(notdir $@)


# Test: links -> children comments
link_test: $(SC_LINK)

$(SRC_LINK):
	+make -C $(dir $@) $(notdir $@) N=$(NQ_LINK)

$(GT_LINK): $(SRC_LINK) | $(TESTDIR)/
	awk -F ';' '{q++; for (i=2;i<NF;i++){print "Q"q"\t-\t"$$i"\t"1;}}' $< > $@

$(RE_LINK): $(SRC_LINK) $(SEARCHER_EXE) | $(TESTDIR)/
	cat $< | cut -d ';' -f 1 | $(FORMAT_QUERY) | $(SEARCHER) | grep '^\([0-9]\+:\|$$\)' | sed 's/://' | awk -F " " '{if ($$0 == "") {q++} else { print "Q"q"\t-\t"$$2"\t"$$1"\t"($(NDOCS)-$$1)"\tlinks"; }}' > $@

$(SC_LINK): $(GT_LINK) $(RE_LINK)
	$(TREC) $^ > $@


# Test: random words of a comment -> this comment
comm_test: $(SC_COMM)

$(SRC_COMM):
	$(eval d := syseval/scores/)
	+make -C $(d) $(subst $(d),,$@)

$(GT_COMM): $(SRC_COMM) | $(TESTDIR)/
	cat $< | cut -f 1 | awk '{q++; print "Q"q"\t-\t"$$0"\t"1;}' > $@

$(RE_COMM): $(SRC_COMM) $(SEARCHER_EXE) | $(TESTDIR)/
	cat $< | cut -f 2 | $(FORMAT_QUERY) | $(SEARCHER) | grep '^\([0-9]\+:\|$$\)' | sed 's/://' | awk -F " " '{if ($$0 == "") {q++} else { print "Q"q"\t-\t"$$2"\t"$$1"\t"($(NDOCS)-$$1)"\tcomms"; }}' > $@

$(SC_COMM): $(GT_COMM) $(RE_COMM)
	$(TREC) $^ > $@



$(TESTDIR)/:
	mkdir -p $@


clean:
	rm -f $(GT_LINK) $(RE_LINK) $(SC_LINK)
#	make -C $(dir $(TREC)) clean



.PHONY: test link_test comm_test clean
