import numpy as np
import pandas as pd
from functools import partial
from networkx import Graph


def get_predictions(node_pairs, *link_predictors):
    return [get_prediction(node_pairs, link_predictor) for link_predictor in link_predictors]


def get_prediction(node_pairs, link_predictor):
    return link_predictor.predict(node_pairs)


def get_dataframe(predictions, predictor_names, with_node_pairs=False):
    df = pd.DataFrame()
    for prediction, predictor_name in zip(predictions, predictor_names):
        if with_node_pairs:
            df['node_pairs'] = [(pred[0], pred[1]) for pred in prediction]
        df[predictor_name] = [pred[2] for pred in prediction]
    return df
