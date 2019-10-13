import sqlite3

DB_PATH="../../../../database.sqlite"

if __name__ == "__main__":

    # Read command-line arguents
    import argparse
    parser = argparse.ArgumentParser(description="Get n link ids")
    parser.add_argument('n', type=int, help="Number of link ids")
    args = parser.parse_args()

    # Connect to DB
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Execute query and print results
    sql_query = """SELECT DISTINCT link_id FROM May2015 ORDER BY created_utc LIMIT %d"""%args.n
    for row in c.execute(sql_query):
        print(row[0])


    conn.close()
