import argparse
import gc

import preprocessing
import models
import training
import evaluation

import numpy as np
from sklearn.model_selection import train_test_split


def main():
    df_raw_data = preprocessing.get_data_db('../../sample_3days.sqlite')
    df_X, df_y = preprocessing.preprocess(df_raw_data)

    df_X.drop(preprocessing.dict_category_columns['text'], axis=1, inplace=True)
    gc.collect()


    indices = np.arange(len(df_X))
    splits = {}
    splits['train'], splits['test'] = train_test_split(indices, test_size=0.1)
    splits['train'], splits['validation'] = train_test_split(splits['train'], test_size=0.1)

    model = models.get_model()
    model = training.train(model, df_X, df_y, splits)
    print(model.score(df_X, df_y))



if __name__ == '__main__':
    main()
