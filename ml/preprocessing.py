import pandas as pd
import sqlite3
from collections import defaultdict

from sklearn.preprocessing import LabelEncoder

"""
Reads the data from the sqlite database or a csv file or whatever into a pandas DataFrame.
Preprocesses said DataFrame and return a DataFrame for the features and one for
the labels.
"""

# Associates type of columns to column names
dict_category_columns = {
    'object': [
        'subreddit_id', 
        'link_id', 
        'name', 
        'author_flair_css_class',
        'author_flair_text',
        'subreddit',
        'id',
        'removal_reason',
        'author',
        'distinguished',
        'parent_id',
    ],
    'numeric': [
        'ups',
        'score_hidden',
        'gilded',
        'downs',
        'score',
    ],
    'boolean': [
        'archived',
        'edited',
        'controversiality',
    ],
    'date': [
        'created_utc',
        'retrieved_on'
    ],
    'text': [
        'body'
    ],
}

def get_data_db(path_to_db):
    connection = sqlite3.connect(path_to_db)

    data = pd.read_sql_query("""
        SELECT *
        FROM May2015
        LIMIT 100000
    """, connection)

    return data



def preprocess(df_raw):
    print(df_raw.info())

    # Columns to encode with a label encoder (object -> id)
    object_columns = dict_category_columns['object']



    dict_fillna_values = {}
    for column in object_columns:
        dict_fillna_values[column] = 'None'


    target_columns = ['ups', 'score_hidden', 'downs', 'score']
    feature_columns = [
        column 
        for column in df_raw.columns 
        if column not in target_columns
    ]



    #for col in df_raw.columns:
    #    print(df_raw[col].describe(), '\n')

    df_raw.fillna(dict_fillna_values, inplace=True)
    #print(df_raw['author_flair_css_class'].head().fillna('Kek'))
    #df_raw[object_columns].fillna('None')


    # Dictionary of LabelEncoder, associating to each column its fitted
    # LabelEncoder
    dict_label_encoder = defaultdict(LabelEncoder)
    df_raw[object_columns] = df_raw[object_columns].apply(
        lambda column: dict_label_encoder[column.name].fit_transform(column)
    )

    X = df_raw[feature_columns]
    y = df_raw[target_columns]

    del df_raw

    return X, y

def main():
    return

if __name__ == '__main__':
    main()
