import sqlite3


DB_PATH = "../../../database.sqlite"

def main():
    
    conn = sqlite3.connect(DB_PATH)
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
 
    args = parser.parse_args()
    main()


