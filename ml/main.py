import argparse
import gc

import preprocessing
import models
import training
import evaluation


def main():
    df_raw_data = preprocessing.get_data_db('../../sample_3days.sqlite')

    df_X, df_y = preprocessing.preprocess(df_raw_data)

    gc.collect()

    print(df_X.head(), df_y.head())
    print(df_X.info())

    model = models.get_model()

    training.train(model, df_X, df_y)
    model.fit(df_X, df_y)



if __name__ == '__main__':
    main()
