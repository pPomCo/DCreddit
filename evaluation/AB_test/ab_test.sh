#! /bin/bash


# Settings
SIM=bm25
INDEXDIR=../../indexation/indexes/$SIM


# Use personalization
ab=`expr $RANDOM % 2`
test $ab -eq 0 && run_id="A"
test $ab -eq 1 && run_id="B"

# Use reordering
reord=`expr $RANDOM % 3`
test $reord -eq 0 && run_id="${run_id}_no"
test $reord -eq 1 && run_id="${run_id}_ups"
test $reord -eq 2 && run_id="${run_id}_normups"

# Generate uniq_id
run_id="${run_id}_$RANDOM"

# Run A/B test
python3 ab_app.py $INDEXDIR --sim $SIM $run_id