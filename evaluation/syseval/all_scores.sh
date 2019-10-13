#! /bin/sh

# Usage: all_scores.sh n_kws num_col

usage() {
    echo "usage: $0 n_kws num_col >&2"
}
test $# -ne 2 && usage && exit 1
n_kw="$1"
num_col="$2"


# CSV header
echo "name $n_kw"

# CSV rows
for i in 1 2 3
do
    echo -n "`cat scores/rank3.csv | tail -n +$i | head -n 1 | cut -f 1 | cut -d '/' -f 3 | cut -d '-' -f 1` "
    for r in $n_kw
    do
    	echo -n "`cat scores/rank$r.csv | tail -n +$i | head -n 1 | cut -f $num_col` "
    done
    echo ""
done
