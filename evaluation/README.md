# Evaluation

## System evaluation

We use *trec_eval*, the [TREC](https://trec.nist.gov/) evaluation tool.

### Compiling the *trec_eval* software

*trec_eval* will be compiled, if necessary, while running tests. You may want to compile it by yourself using:

	# Compile trec_eval
	make -C trec_eval.8.1
	
*Note: compilation produces some warnings.*

### Running tests

In order to test the default model (bm25 with no reordering), you simply want to type:

	# Test the bm25 with no reordering
	make

To test others models you may want to use

	# Test the TFxIDF with 'ups' reordering
	make SIMILARITY=tfxidf REORDERING=ups

If you just want to compare our models, that is TFxIDF, LM and BM25, using 'ups' or no reordering, you may want to start the following shell script:

	# Run all tests and print a CSV-like output
	./all_tests.sh

### Results

We note that results differ, depending on which ground truth we consider.

On the one hand, the *bm25* (probabilistic model) got the highest score with the comment-test (picking some random words from a comment, we expect to find it back). We already discuss this result in [syseval/](syseval/README.md).

![Results](images/comm-test.png  "Results (comment-test)")

On the other hand, the *lm* (language model) got the highest score with the link-test (querying with the title of a link, we expect to find its child comments).

We explain this distinction by the quality of the considered ground truth. For the comment-test, we collect random words, thus their position in the query is of no importance. On the contrary, for the link-test, we query with titles, which are likely to contain sequences of words, thus their relative positions are a relevant feature.

![Results](images/link-test.png  "Results (link-test)")

Measures are about half as good on the *TFxIDF* (vectorial model) as on the other models. Thus we can safely abandon this approach.

Moreover, we can note that reordering using 'ups' produces lower score than no reordering. It's obvious that when searching a low-ups document, the reordering hinders finding it back.

Furthermore, we note that the MAP (Mean Average Precision) metric produces much better scores for the comment-test than for the link-test (*resp.* 0.74 and 0.013), while the P@n metrics are much more related.

### Normalized 'ups' reordering

We don't test the *normalized 'ups'* reordering, since it takes a long time. Our implementation is not scalable, and we have to fix it before expecting to test it over 1000 queries.
