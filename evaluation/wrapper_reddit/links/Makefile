

LINKS = $(shell python3 get_link_ids.py 1000)
JSONS = $(foreach link, $(LINKS), data/json/$(link).json)
TITLES= $(foreach link, $(LINKS), data/title/$(link).txt)
SLEEP = 1

all: $(TITLES)


data/json/%.json: | data/json/
	-wget -q https://www.reddit.com/comments/$(subst t3_,,$*)/.json -O $@
	$(WAIT)

data/title/%.txt: data/json/%.json | data/title/
	cat $^ | sed 's/, "/\n "/g'| grep '"title":'  | sed 's/ "title": //' | sed 's/"//g' > $@

data/json/ data/title/:
	mkdir -p $@



preview: $(JSONS)
	cat $^ | sed 's/, "/\n "/g'| grep '"title":'  | sed 's/ "title": //'


clean:
	rm -fr data/


.PHONY: all clean preview
