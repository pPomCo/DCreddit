# You may need to adjust the following settings

PROJECT_DIR = /projets/M2DC
# Database
DB = $(PROJECT_DIR)/data/database.sqlite

# Representation model
SIMILARITY = bm25

# Index directory
INDEXDIR = $(PROJECT_DIR)/index/$(SIMILARITY)/


all: index

index: | $(INDEXDIR)
	python3 indexer.py $(DB) $(INDEXDIR) --sim $(SIMILARITY)

search:
	python3 searcher.py $(INDEXDIR) --sim $(SIMILARITY)

$(INDEXDIR):
	mkdir -p $@

clean:
	rm -fr $(INDEXDIR)

.PHONY: all index search
