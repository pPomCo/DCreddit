import sqlite3


DB_PATH = "../../../database.sqlite"

def main():
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c2 = conn.cursor()

    user_query = """SELECT DISTINCT author FROM May2015 ORDER BY author"""
    for row in c.execute(user_query):
        author = row[0]
        comms_query = """SELECT SUM(ups), COUNT(name) FROM May2015 WHERE author='%s'"""%author
        infos = list(c2.execute(comms_query))[0]
        print(";".join([str(x) for x in [author]+list(infos)]))
   
    conn.close()



if __name__ == "__main__":

    # Read command-line arguments
    import argparse
    parser = argparse.ArgumentParser(
        description="Create a CSV with some user info")
    args = parser.parse_args()

    main()


