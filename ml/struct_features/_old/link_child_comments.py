import sqlite3


def main(k, db_path):
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c2 = conn.cursor()

    link_query = """SELECT DISTINCT link_id FROM May2015 ORDER BY link_id"""
    for row in c.execute(link_query):
        link_id = row[0]
        comms_query = """SELECT name, ups FROM May2015 WHERE parent_id="%s" ORDER BY ups LIMIT %d"""%(link_id,k)
        comments = list(c2.execute(comms_query))
        print(";".join([r[0] for r in [row]+comments]))
   
    conn.close()



if __name__ == "__main__":

    # Read command-line arguments
    import argparse
    parser = argparse.ArgumentParser(
        description="Create a CSV which associate link_ids to there top-k child comments (ranking using 'ups')")
    parser.add_argument('k', type=int, nargs='?', default=10,
                        help='Number of comments to attach to a link')
    parser.add_argument('--db', type=str, help="Database path")
 

    args = parser.parse_args()

    main(k=args.k, db_path=args.db)


