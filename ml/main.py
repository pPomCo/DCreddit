import argparse
import gc

import preprocessing
import models
import training
import evaluation

import numpy as np
from sklearn.model_selection import train_test_split


def main():
    df_data = preprocessing.get_data_db('../../sample_3days.sqlite')
    preprocessing.fill_missing_values(df_data)
    df_data = preprocessing.preprocess(df_data)

    #df_data.drop(preprocessing.dict_category_columns['text'], axis=1, inplace=True)

    target_columns = preprocessing.target_columns
    feature_columns = [
        column 
        for column in df_data.columns 
        if column not in target_columns
    ]
    target_columns = ['ups']

    print(target_columns, '\n')
    print(feature_columns)


    indices = np.arange(len(df_data))
    splits = {}
    splits['train'], splits['test'] = train_test_split(indices, test_size=0.1)
    splits['train'], splits['validation'] = train_test_split(splits['train'], test_size=0.1)

    model = models.get_model()
    model = training.train(
        model, 
        df_data[feature_columns], 
        df_data[target_columns], 
        splits
    )
    print(model.score(df_data[feature_columns], df_data[target_columns]))



if __name__ == '__main__':
    main()
