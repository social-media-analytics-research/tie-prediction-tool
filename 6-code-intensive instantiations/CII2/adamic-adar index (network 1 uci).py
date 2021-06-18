#1 Load neccessray Libraries
import random
import networkx as nx
from sklearn.metrics import roc_auc_score
from datetime import datetime

#2 Load graphml network
G = nx.read_graphml('uci-1899-directed.graphml')

#3 Display number of ties
a = G.number_of_nodes() 
t = G.number_of_edges()
print("Number of nodes : %d" % a)
print("Number of edges : %d" % t)

#4 Create seed and time tracker 
random.seed(0)
t1 = datetime.now()

#5 Create a test set of 95 percent from G
edges_to_remove_from_G = 0.05
removed_edges_from_G = random.sample(G.edges(), int(edges_to_remove_from_G * G.number_of_edges()))
G_test = G.copy()
G_test.remove_edges_from(removed_edges_from_G)
edge_subset_G_size = len(list(removed_edges_from_G))
print("Number of edges deleted : %d" % edge_subset_G_size)
print("Number of edges remaining : %d" % (t - edge_subset_G_size))

#6 Create a train set of 80 percent from G_test
edges_to_remove_from_G_test = 0.201
removed_edges_from_G_test = random.sample(G_test.edges(), int(edges_to_remove_from_G_test * G_test.number_of_edges()))
G_train = G_test.copy()
G_train.remove_edges_from(removed_edges_from_G_test)
edge_subset_G_test_size = len(list(removed_edges_from_G_test))
print("Number of edges deleted : %d" % edge_subset_G_test_size)
print("Number of edges remaining : %d" % (t - edge_subset_G_size - edge_subset_G_test_size))

#6 Transform G_train and G_test to undirected
G_train = G_train.to_undirected()
G_test = G_test.to_undirected()

#7 Calculate AA AUC
pred_aa_train = list(nx.adamic_adar_index(G_train))
pred_aa_test = list(nx.adamic_adar_index(G_test))
score_aa, label_aa = zip(*[(s, (u,v) in removed_edges_from_G) for (u,v,s) in pred_aa_test])
auc_aa = roc_auc_score(label_aa, score_aa)

#8 Print AUC and prediciton calculation time
t2 = datetime.now()
delta = t2 - t1
print(auc_aa, delta.seconds)
