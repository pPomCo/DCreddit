#! /bin/sh

# Execute tests for each model/reordering
# Print a csv with map and P5->P20


MODELS="tfxidf lm bm25"
REORDS="no ups" # normups"
SCORES="map P5 P10 P15 P20"

# Make tests
for m in $MODELS
do
    for r in $REORDS
    do
	f=tests/$m/$r/links_out.test
	test ! -f $f  && make $f MODEL=$m REORDERING=$r -j 4
	f=tests/$m/$r/comm_out.test
	test ! -f $f  && make $f MODEL=$m REORDERING=$r -j 4
    done
done







# CSV header
echo -n "model\treord\t"
for sc in $SCORES
do
    echo -n "l_$sc\tc_$sc\t"
done
echo ""



# Read score in trec_eval output file
read_score() { # $1=filename, $2=scorename
    grep "$2 " $1 | cut -f 3 | awk 'BEGIN{ORS="\t"}{print $0;}'
}


# CSV rows
for m in $MODELS
do
    for r in $REORDS
    do
	echo -n "$m\t$r\t"
	for sc in $SCORES
	do
	    read_score tests/$m/$r/links_out.test $sc
	    read_score tests/$m/$r/comm_out.test $sc
	done
	echo ""
    done
done


exit 0
