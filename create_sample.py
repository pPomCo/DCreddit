import sys
import argparse
import sqlite3

def main(path_to_db, path_to_sample, nb_samples):
    connection_sample = sqlite3.connect(path_to_sample)
    cursor_sample = connection_sample.cursor()

    cursor_sample.execute('''
        ATTACH DATABASE ? AS full_db
    ''', [path_to_db])

    cursor_sample.execute('''
        CREATE TABLE May2015 AS
            SELECT *
            FROM full_db.May2015
            LIMIT ?
    ''', [nb_samples])

    connection_sample.commit()

    connection_sample.close()

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument(
        "path_to_db", 
        help="Path to the whole database file", 
    )
    arg_parser.add_argument(
        "path_to_sample", 
        help="Path to the sample database file to create", 
    )
    arg_parser.add_argument(
        "nb_samples", 
        type=int,
        help="Number of rows to sample",
    )

    args = vars(arg_parser.parse_args())

    main(args['path_to_db'], args['path_to_sample'], args['nb_samples'])
