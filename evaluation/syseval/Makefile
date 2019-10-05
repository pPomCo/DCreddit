# Ground truth
N_KWS = 1 2 3 4 5 6 7 8 9 10 12 14 16 # Number of keywords
N_QR = 1000 # Number of queries

# Evaluated
SEARCHER = python3 ../../indexation/searcher.py
MODELS = tfxidf lm bm25
REORDER = no #ups normups
IDS = $(foreach m, $(MODELS), $(foreach r, $(REORDER), $(m)-$(r)))


all: scores-freq.csv scores-rank.csv

scores-freq.csv: $(foreach nkw, $(N_KWS), scores/rank$(nkw).csv) | scores/
	./all_scores.sh "$(N_KWS)" 2 > $@

scores-rank.csv: $(foreach nkw, $(N_KWS), scores/rank$(nkw).csv) | scores/
	./all_scores.sh "$(N_KWS)" 3 > $@

scores/rank%.csv:
	+make -C scores $(notdir $@) N_KW=$*

clean:
	rm -f scores-freq.csv scores-rank.csv
	+$(foreach nkw, $(N_KWS), make -C scores clean N_KW=$(nkw);)


.PHONY: all clean
