N = 1000

LINKS = $(shell python3 get_link_ids.py $(N))
JSONS = $(foreach link, $(LINKS), data/json/$(link).json)
POSTS = $(foreach link, $(LINKS), data/posts/$(link).txt)
GTRUTH = gtruth_link_$(N).csv



all: $(GTRUTH)

download: $(JSONS)

data/json/%.json: | data/json/
	-wget -q https://www.reddit.com/comments/$(subst t3_,,$*)/.json -O $@

data/title/%.txt: data/json/%.json | data/title/
	cat $^ | sed 's/, "/\n "/g'| grep '"title":' | head -n 1 | sed 's/ "title": //' | sed 's/\(;\|"\)/ /g'> $@

data/posts/%.txt: data/title/%.txt | data/posts/
	(cat "$^" && python3 get_link_posts.py $*) | \
	  awk '{s=s";"$$0;}END{print s;}' > $@

$(GTRUTH): $(POSTS)
	cat $^ | sed 's/; //' | grep -v '^;' > $@

data/json/ data/title/ data/posts/:
	mkdir -p $@



preview: $(JSONS)
	cat $^ | sed 's/, "/\n "/g'| grep '"title":'  | sed 's/ "title": //'


clean:
	rm -fr data/


.PHONY: all download clean preview

