#[1] Preprocessing============================================================

#1 Load neccessray Libraries
import random, networkx as nx, pandas as pd, matplotlib.pyplot as plt, numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
from sklearn.utils import shuffle
from sklearn import metrics
from datetime import datetime

#2 Load graphml network
twt = nx.read_graphml('twitter-745-directed-project(numeric).graphml')

#3 Display number of edges and nodes
a = twt.number_of_nodes() 
t = twt.number_of_edges()
print("Number of nodes : %d" % a)
print("Number of edges : %d" % t)

#4 Create seed and time tracker 
random.seed(0)
t1 = datetime.now()

#5 Create a test set of 95 percent from G
edges_to_remove_from_twt = random.sample(twt.edges(), int(0.05 * twt.number_of_edges()))
twt_test = twt.copy()
twt_test.remove_edges_from(edges_to_remove_from_twt)
print("Number of edges deleted : %d" % len(edges_to_remove_from_twt))
print("Number of edges remaining : %d" % (twt_test.number_of_edges()))

#6 Transform twt_test to undirected
twt_test = twt_test.to_undirected()

#7 Calculate JC and PA AUC as features for negative edges
pred_jc_test_neg = list(nx.preferential_attachment(twt_test))
pred_pa_test_neg = list(nx.jaccard_coefficient(twt_test))

#8 Calculate JC and PA AUC as features for positive edges
pred_jc_test_pos = list(nx.preferential_attachment(twt_test,twt_test.edges()))
pred_pa_test_pos = list(nx.jaccard_coefficient(twt_test, twt_test.edges()))

#9 Combine negative and positive predictions
pred_jc_test_total = (pred_jc_test_neg + pred_jc_test_pos)
pred_pa_test_total = (pred_pa_test_neg + pred_pa_test_pos)
print("Number of negative edges : %d" % len(pred_jc_test_neg))
print("Number of positive edges : %d" % len(pred_jc_test_pos))

#[2] Dataframe================================================================

#1 Create score dataframe df
dict = {          
        'tuple1': [elem1[:2] for elem1 in pred_jc_test_total],
        'tuple2': [elem2[:2] for elem2 in pred_pa_test_total],
        'jc_score_full': [elem[:3] for elem in pred_jc_test_total],
        'pa_score_full': [elem[:3] for elem in pred_pa_test_total],
        'jc_score': [elem[2] for elem in pred_jc_test_total],
        'pa_score': [elem[2] for elem in pred_pa_test_total],
      }

twt_test_df = pd.DataFrame(dict)

labels = list()

#2 Calculate labels and append labels to dataframe df
for val in twt_test_df['tuple1']: 
    if twt_test.has_edge(val[0],val[1]):
        labels.append(1)
    else:
        labels.append(0) 
twt_test_df.insert(6,"label",pd.DataFrame(labels))
index = twt_test_df.index        
twt_test_df = shuffle(twt_test_df)
twt_test_df.index = index

#3 Print dataframe for test
pd.set_option('display.max_columns', 7)
print(twt_test_df)
print("The data is consistent", (twt_test_df['tuple1'] == twt_test_df['tuple2']))

#[3] Prediciton===============================================================

#1 Create test set for logistic regression model
X_test = twt_test_df[['jc_score', 'pa_score']]
Y_test = twt_test_df['label']

# Create train set for logistic regression model (set 20 percent of ties from tes to "0")
twt_train_df = twt_test_df.drop(twt_test_df.query('label == 1').sample(frac=0.2).index)
X_train = twt_train_df[['jc_score', 'pa_score']]
Y_train = twt_train_df['label']

#2 Apply logistic regression model
logistic_regression= LogisticRegression()
logistic_regression.fit(X_train,Y_train)

#3 Retrieve AUC value
auc = roc_auc_score(Y_test,logistic_regression.decision_function(X_test))
t2 = datetime.now()
delta = t2 - t1
print(auc, delta.seconds)