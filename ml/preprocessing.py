import sqlite3
from collections import defaultdict

import numpy as np
import pandas as pd
import joblib
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer

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

target_columns = [
    'ups', 
    'score_hidden', 
    'downs', 
    'score',
]

def get_data_db(path_to_db):
    connection = sqlite3.connect(path_to_db)

    data = pd.read_sql_query("""
        SELECT *
        FROM May2015
        LIMIT 10000
    """, connection)

    return data

# Fill missing values
def fill_missing_values(df):
    dict_fillna_values = {}
    for column in dict_category_columns['object']:
        dict_fillna_values[column] = 'None'

    df.fillna(dict_fillna_values, inplace=True)

# Encode object columns, dummy categorical columns, scale scalar columns 
def preprocess(df):
    object_columns = dict_category_columns['object']

    #target_columns = ['ups', 'score_hidden', 'downs', 'score']
    #feature_columns = [
    #    column 
    #    for column in df.columns 
    #    if column not in target_columns
    #]


    # Encode object columns to ids
    dict_label_encoder = defaultdict(LabelEncoder)
    df[object_columns] = df[object_columns].apply(
        lambda column: dict_label_encoder[column.name].fit_transform(column)
    )
    #joblib.dump(dict_label_encoder, 'dict_label_encoder.pkl')
    
    # Cyclical encoding of day_of_week and hour_of_day
    fraction_dayofweek = 2*np.pi * (
        pd.to_datetime(df['created_utc'], unit='s').dt.dayofweek / 7
    )
    fraction_hourofday = 2*np.pi * (
        pd.to_datetime(df['created_utc'], unit='s').dt.hour / 24
    )
    df['day_of_week_sin'] = np.sin(fraction_dayofweek)
    df['day_of_week_cos'] = np.cos(fraction_dayofweek)
    df['hour_of_day_sin'] = np.sin(fraction_hourofday)
    df['hour_of_day_cos'] = np.cos(fraction_hourofday)

    # TF-IDF encoding of the comments body
    tfidf_vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
    tfidf = tfidf_vectorizer.fit_transform(df['body'])
    df_tfidf = pd.DataFrame(
        tfidf.toarray(), 
        columns=tfidf_vectorizer.get_feature_names()
    )
    df = pd.concat([df, df_tfidf], axis=1)

    df.drop('body', axis=1, inplace=True)

    return df

def main():
    return

if __name__ == '__main__':
    main()
