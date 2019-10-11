import sqlite3

DB_PATH="../../../../database.sqlite"

if __name__ == "__main__":

    # Read command-line arguents
    import argparse
    parser = argparse.ArgumentParser(description="Get link posts (first messages)")
    parser.add_argument('lid', type=str, help="ID of the link")
    args = parser.parse_args()

    # Connect to DB
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Execute query and print results
    sql_query = """SELECT name FROM May2015 WHERE link_id = '%s'"""%args.lid
    for row in c.execute(sql_query):
        print(row[0])


    conn.close()
