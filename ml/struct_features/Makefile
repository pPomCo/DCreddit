# Files
LCHILDREN = link_child_comments.csv
ANCESTORS = comment_ancestors.csv
BROTHERS  = anterior_brothers.csv
UINFOS    = user_infos.csv

CSVs = $(UINFOS) $(ANCESTORS) $(LCHILDREN) $(BROTHERS) 




extract_all: $(CSVs)



$(LCHILDREN):
	python3 link_child_comments.py 10 > $@

$(ANCESTORS):
	python3 comment_ancestors.py > $@

$(BROTHERS):
	python3 anterior_brothers.py > $@

$(UINFOS):
	python3 user_info.py > $@


clean:
	rm -f link_child_comments.csv

.PHONY: extract_all clean
