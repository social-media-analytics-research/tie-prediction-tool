from sklearn.base import BaseEstimator


def get_X_y(df, columns_drop=['node_pairs', 'label'], label_drop='label'):
    X = df.drop(columns_drop, axis=1)
    y = df[label_drop]
    return X, y