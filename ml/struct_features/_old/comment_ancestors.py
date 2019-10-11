import sqlite3



def main(db_path):
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c2 = conn.cursor()
    c3 = conn.cursor()


    comm_query = """SELECT name, parent_id FROM May2015 ORDER BY name"""
    for row in c.execute(comm_query):
        is_leaf_query = """SELECT COUNT(*) FROM May2015 WHERE parent_id='%s'"""%row[0]
        if int(list(c2.execute(is_leaf_query))[0][0]) == 0:
            ancestors = [row[0]]
            parent_id = row[1]
            is_searching = True
            while is_searching:
                q = """SELECT name, parent_id FROM May2015 WHERE name='%s'"""%parent_id
                c = list(c3.execute(q))
                if len(c) > 0:
                    ancestors.append(c[0][0])
                    parent_id = c[0][1]
                else:
                    is_searching = False
            print(";".join(ancestors))
            
    conn.close()

if __name__ == "__main__":

    # Read command-line arguments
    import argparse
    parser = argparse.ArgumentParser(
        description="Create a CSV which associate comment_id to its k closest ancestors")
    parser.add_argument('--db', type=str, help="Database path")
  
    args = parser.parse_args()
    main(args.db)


