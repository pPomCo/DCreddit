# Database
DB = /projets/M2DC/data/database.sqlite

# Files
LCHILDREN = link_child_comments.csv
ANCESTORS = comment_ancestors.csv
BROTHERS  = anterior_brothers.csv
UINFOS    = user_infos.csv

CSVs = $(UINFOS) $(ANCESTORS) $(LCHILDREN) $(BROTHERS) 




extract_all: $(CSVs)



$(LCHILDREN):
	python3 link_child_comments.py 10 --db $(DB) > $@

$(ANCESTORS):
	python3 comment_ancestors.py --db $(DB) > $@

$(BROTHERS):
	python3 anterior_brothers.py --db $(DB) > $@

$(UINFOS):
	python3 user_info.py --db $(DB) > $@


clean:
	rm -f $(LCHILDREN) $(ANCESTORS) $(BROTHERS) $(UINFOS)

.PHONY: extract_all clean
