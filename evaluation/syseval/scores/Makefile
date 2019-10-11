# Database
DB = ../../../data/sample100k.sqlite

# Indexation directory
INDEXDIR = ../../../indexation

# Ground truth
N_KW = 5
N_QR = 1000 # Number of queries
GTRUTH = out/$(N_KW)/gtruth.csv

# Evaluated
SEARCHER = python3 $(INDEXDIR)/searcher.py
MODELS = tfxidf lm bm25
REORDER = no #ups normups
IDS = $(foreach m, $(MODELS), $(foreach r, $(REORDER), $(m)-$(r)))


all: scores/rank$(N_KW).csv

rank$(N_KW).csv: $(foreach id, $(IDS), out/$(N_KW)/$(id).txt)
	python3 ../compute_scores.py out/$(N_KW)/gtruth.csv $^ > $@

out/$(N_KW)/%-no.txt: $(GTRUTH) | out/$(N_KW)/
	(cat $(GTRUTH) | cut -f 2 && echo "")  | $(SEARCHER) $(INDEXDIR)/indexes/$* --sim $* --short | grep '^\([0-9]\+:\|$$\)' > $@

out/$(N_KW)/%-ups.txt: $(GTRUTH) | out/$(N_KW)/
	(cat $(GTRUTH) | cut -f 2 && echo "")  | $(SEARCHER) $(INDEXDIR)/indexes/$* --sim $* --reorder ups --short | grep '^\([0-9]\+:\|$$\)'  > $@

out/$(N_KW)/%-normups.txt: $(GTRUTH) | out/$(N_KW)/
	(cat $(GTRUTH) | cut -f 2 && echo "")  | $(SEARCHER) $(INDEXDIR)/indexes/$* --sim $* --reorder normups --short | grep '^\([0-9]\+:\|$$\)'  > $@



$(GTRUTH): | out/$(N_KW)/
	python3 ../mk_ground_truth.py $(DB) $(N_QR) $(N_KW) > $@


out/$(N_KW)/ :
	mkdir -p $@





clean:
	rm -fr out/ rank$(N_KW).csv


.PHONY: all clean
.PRECIOUS: $(GTRUTH) rank$(N_KW).csv
