import random
import queue
import networkx as nx
random.seed(42)  # For reproducibility


def sampling_by_percentage(G, percentage):
    if percentage < 0 and percentage > 1:
        raise ValueError('Invalid percentage value. It must be among 0 and 1!')
    return sampling_by_count(G, G.number_of_edges() * percentage)


def sampling_by_count(G, linksCount):
    if linksCount > G.number_of_edges():
        raise ValueError('Invalid links count value. It must be smaller than the maximum graph edges!')

    adjustedGraph = G.copy()
    for i in range(G.number_of_edges() - int(linksCount)):
        edgeToRemove = random.choice(list(adjustedGraph.edges()))
        adjustedGraph.remove_edge(*edgeToRemove)
    return adjustedGraph


def sampling_by_time(G, timepoint):
    # Note: Implement for sampling along time dimension.
    pass


def find_all_missing_edges(G):
    return list(nx.non_edges(G))


def find_missing_edges_at_distance(G, distance, undirected=True):
    missingLinks = []
    for node in G.nodes():
        missingNodesAtU = find_from_node(G, node, distance)
        missingLinks.extend(missingNodesAtU)

    if(undirected):
        missingLinks = list(remove_reversed_duplicates(missingLinks))
    return missingLinks


def find_from_node(G, u, distance):
    missingLinks = []
    visited = [False] * (G.number_of_nodes() + 1)
    q = queue.Queue()
    q.put(u)
    visited[u] = True

    for i in range(1, distance + 1):
        newFound = queue.Queue() 
        while not q.empty():
            temp = q.get()
            for v in G.neighbors(temp):
                if not visited[v]:
                    newFound.put(v)
                    visited[v] = True
        q = newFound

    while not q.empty():
        v = q.get()
        if not G.has_edge(u, v):
            missingLinks.append((u, v))

    return missingLinks


def remove_reversed_duplicates(missingLinks):
    seenLinks = set()
    for link in missingLinks:
        if link not in seenLinks:
            seenLinks.add(link[::-1])
            yield link
