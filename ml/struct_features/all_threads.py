"""
Print a very-very large CSV containing all ascending path, from each comment
to its link, using the parent_id relation.

It is clearly untractable.
Consider this code as an example of 1. FeatureExtractor use, and 2. batch scan
of the neo4j database.
"""
from f_extractor import FeatureExtractor as FX





if __name__ == "__main__":

    # Read command-line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Print all threads (from any comment to its link)")
    parser.add_argument('uri', type=str, help="DB's URI (eg. bolt://localhost:7687)")
    parser.add_argument('user', type=str, help="User name")
    parser.add_argument('passw', type=str, help="Password")

    args = parser.parse_args()


    # Load the feature extractor    
    fx = FX(args.uri, args.user, args.passw)


    # Work in batch using STARTS WITH on the index :Commentaire(nom)
    letters = "abcdefghijklmnopqrstuvwxyz0123456789"
    for x0 in letters:
        for x1 in letters:
            for x2 in letters:
                prefix = 't1_cq%s%s%s'%(x0,x1,x2)
                res = fx.execute(" MATCH path=(c:Commentaire)-[:Parent*2..]->(:Post)"
                                 " WHERE c.nom STARTS WITH {startwith}"
                                 " WITH NODES(path) AS ns"
                                 " RETURN ns",
                                 startwith=prefix)
                if res != []:
                    print("\n".join(["\t".join([n['nom'] for n in d['ns']]) for d in res]))
                    

    
