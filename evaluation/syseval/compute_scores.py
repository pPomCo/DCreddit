"""
Compute scores (off-line evaluation)


Rank score
    Idea:
        Relevant documents should be as top-ranked as possible.
    Prerequisites:
        One relevent document per query
    Paramters:
        k: Number of results per query
        n: Number of keywords per query
    Output:
        Frequence of queries that contain the document in their top-k results 
        Average rank of the document (when it appear in the top-k results)
"""



def read_gtruth(gtruth_file):
    """Read ground truth file

    Format: relevant document for query i = first word of the i-th line
    """
    y = []
    with open(gtruth_file, 'r') as f:
        for line in f:
            y.append(line.split()[0])
    return y

def read_result(result_file):
    """Read result files

    Format: output for each query are separated with a single blank line
            there is a single blank line at the beginning of the doc
            each data line greps '^[rank]: [doc_id] .*$'
            queries are in the same order as those of the ground truth
    """
    x = []
    with open(result_file, 'r') as f:
        for line in f:
            if line == "\n":
                x.append([])
            else:
                x[-1].append(line.split()[1])
    return x



def index_of(x, X):
    """Index of x in the enumerable X, of None if x not in X"""
    for i, xi in enumerate(X):
        if x == xi:
            return i
    return None


def rank_score(X, y):
    """Compute the frequency and average rank of top-k occurence"""
    acc_rank = 0
    acc_found = 0
    for i, doc_id in enumerate(y):
        rank = index_of(doc_id, X[i])
        if rank is not None:
            acc_rank += rank
            acc_found += 1
    return acc_found/len(y), acc_rank/len(y)
        
    



if __name__ == "__main__":
    
    # Read command-line arguments
    import argparse
    parser = argparse.ArgumentParser(
        description='Compute "rank" score')
    parser.add_argument('gtruth', type=str,
                        help="Ground truth")
    parser.add_argument('files', type=str, nargs='+',
                        help="Output search files to compute")
    args = parser.parse_args()

    # Read files
    Xs = {x: read_result(x) for x in args.files}
    y = read_gtruth(args.gtruth)

    # Compute and print scores (csv-like format)
    for name, X in Xs.items():
        found, rank = rank_score(X,y)
        print(name, found, rank, sep="\t")
