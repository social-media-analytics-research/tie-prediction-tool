import pandas as pd
from functools import partial
from networkx import Graph


def assign_labels(node_set, graph):
    nodes = node_set.copy()
    labels = list(map(partial(assign_label, graph=graph), nodes))
    dataset = concatenate(nodes, labels)
    return dataset


def assign_label(node_pair, graph):
    u, v = node_pair[0], node_pair[1]
    return (int(graph.has_edge(u, v)))


def concatenate(node_set, labels):
    dataset = pd.DataFrame({'node_pairs': node_set, 'label': labels})
    return dataset


def constrain_nodes_by_score(graph, threshold, attribute):
    graph_thresholded = graph.copy()
    nodes_to_remove = list(filter(lambda node: node[1] < threshold, graph_thresholded.nodes.data(attribute)))
    graph_thresholded.remove_nodes_from(nodes_to_remove)
    return graph_thresholded


def constrain_edges_by_score(graph, threshold, attribute):
    graph_thresholded = graph.copy()
    edges_to_remove = list(filter(lambda edge: edge[2] < threshold, graph_thresholded.edges.data(attribute)))
    graph_thresholded.remove_edges_from(edges_to_remove)
    return graph_thresholded
