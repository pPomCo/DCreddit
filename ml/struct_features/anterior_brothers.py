import sqlite3


def main(db_path):
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c2 = conn.cursor()


    comm_query = """SELECT name, parent_id, created_utc FROM May2015 ORDER BY name"""
    for row in c.execute(comm_query):
        comments = [row[0]]
        brother_query = """SELECT name FROM May2015 WHERE parent_id='%s' AND created_utc < %d"""%row[1:]
        for r in c2.execute(brother_query):
            comments.append(r[0])
        print(";".join(comments))
            
    conn.close()

if __name__ == "__main__":

    # Read command-line arguments
    import argparse
    parser = argparse.ArgumentParser(
        description="Create a CSV which associate comment_id to its k closest ancestors")
    parser.add_argument('--db', type=str, help="Database path")
 
    args = parser.parse_args()
    main(args.db)


