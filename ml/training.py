import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

def train(model, df_X, df_y, splits):
    X, y = df_X.values[splits['train']], df_y.values[splits['train']]

    model.fit(df_X, df_y)

    return model

def main():
    return

if __name__ == '__main__':
    main()
