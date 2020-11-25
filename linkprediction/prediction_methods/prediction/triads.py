# triads.py - functions for analyzing triads of a graph
#
# Copyright 2015 NetworkX developers.
# Copyright 2011 Reya Group <http://www.reyagroup.com>
# Copyright 2011 Alex Levenson <alex@isnotinvain.com>
# Copyright 2011 Diederik van Liere <diederik.vanliere@rotman.utoronto.ca>
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Functions for analyzing triads of a graph."""
import itertools
from networkx.utils import not_implemented_for
import networkx as nx

__author__ = '\n'.join(['Alex Levenson (alex@isnontinvain.com)',
                        'Diederik van Liere (diederik.vanliere@rotman.utoronto.ca)'])

__all__ = ['triadic_census']

#: The integer codes representing each type of triad.
#:
#: Triads that are the same up to symmetry have the same code.
TRICODES = (1, 2, 2, 3, 2, 4, 6, 8, 2, 6, 5, 7, 3, 8, 7, 11, 2, 6, 4, 8, 5, 9,
            9, 13, 6, 10, 9, 14, 7, 14, 12, 15, 2, 5, 6, 7, 6, 9, 10, 14, 4, 9,
            9, 12, 8, 13, 14, 15, 3, 7, 8, 11, 7, 12, 14, 15, 8, 14, 13, 15,
            11, 15, 15, 16)

#: The names of each type of triad. The order of the elements is
#: important: it corresponds to the tricodes given in :data:`TRICODES`.
TRIAD_NAMES = ('003', '012', '102', '021D', '021U', '021C', '111D', '111U',
               '030T', '030C', '201', '120D', '120U', '120C', '210', '300')


#: A dictionary mapping triad code to triad name.
TRICODE_TO_NAME = {i: TRIAD_NAMES[code - 1] for i, code in enumerate(TRICODES)}


def _tricode(G, v, u, w):
    """Returns the integer code of the given triad.

    This is some fancy magic that comes from Batagelj and Mrvar's paper. It
    treats each edge joining a pair of `v`, `u`, and `w` as a bit in
    the binary representation of an integer.

    """
    combos = ((v, u, 1), (u, v, 2), (v, w, 4), (w, v, 8), (u, w, 16),
              (w, u, 32))
    return sum(x for u, v, x in combos if v in G[u])


@not_implemented_for('undirected')
def triadic_enumeration(G, triads: set([])):
    """Determines the triadic enumeration of a directed graph.

    Parameters
    ----------
    G : digraph
       A NetworkX DiGraph
    triads : set
       A set of list with triads as strings

    Returns
    -------
    enumeration : dict
       Dictionary with triad names as keys and occurrences as tuples.

    Notes
    -----
    This algorithm has complexity $O(m)$ where $m$ is the number of edges in
    the graph.

    See also
    --------
    triad_graph

    References
    ----------
    .. [1] Vladimir Batagelj and Andrej Mrvar, A subquadratic triad census
        algorithm for large sparse networks with small maximum degree,
        University of Ljubljana,
        http://vlado.fmf.uni-lj.si/pub/networks/doc/triads/triads.pdf

    """
    if not isinstance(triads, set):
        return None
    for triad in triads:
        if triad not in TRIAD_NAMES:
            return None
    #: A dictionary mapping triad code to triad name.
    TRICODE_TO_NAME = {i: TRIAD_NAMES[code - 1]
                       for i, code in enumerate(TRICODES)}

    triad_nodes = {name: set([]) for name in triads}
    m = {v: i for i, v in enumerate(G)}
    for v in G:
        vnbrs = set(G.pred[v]) | set(G.succ[v])
        for u in vnbrs:
            if m[u] > m[v]:
                unbrs = set(G.pred[u]) | set(G.succ[u])
                neighbors = (vnbrs | unbrs) - {u, v}
                not_neighbors = set(G.nodes()) - neighbors - {u, v}
                # Find dyadic triads
                if bool(set(['102', '012']).intersection(triads)):
                    for w in not_neighbors:
                        if v in G[u] and u in G[v] and '102' in triads:
                            triad_nodes['102'].add(tuple(sorted([u, v, w])))
                        elif '012' in triads:
                            triad_nodes['012'].add(tuple(sorted([u, v, w])))
                for w in neighbors:
                    code = _tricode(G, v, u, w)
                    current_triad = TRICODE_TO_NAME[code]
                    if current_triad in triads and (
                        m[u] < m[w] or (m[v] < m[w] < m[u] and
                                        v not in G.pred[w] and
                                        v not in G.succ[w])
                    ):
                        triad_nodes[current_triad].add(
                            tuple(sorted([u, v, w]))
                        )
    if '003' in triads:
        # find null triads
        all_tuples = set()
        for s in triad_nodes.values():
            all_tuples = all_tuples.union(s)
        triad_nodes['003'] = set(
            itertools.combinations(G.nodes(), 3)
        ).difference(all_tuples)
    return triad_nodes


def get_missing_edges_for_bt(subgraph: nx.DiGraph):
    """Get missing edge for balance theory."""
    edges = []
    for node in subgraph.nodes:
        for node_neighbor in subgraph.neighbors(node):
            for neighbors_neighbor in subgraph.neighbors(node_neighbor):
                if neighbors_neighbor != node and \
                        not subgraph.has_edge(node, neighbors_neighbor):
                    edges.append((node, neighbors_neighbor))
    return edges


if __name__ == "__main__":
    existing_graph = nx.DiGraph()
    existing_edges = [
        ('A', 'B'), ('B', 'C'),
        ('C', 'A'),
        ('A', 'C'),
        ('C', 'B'),
        ('B', 'A'),
    ]
    existing_graph.add_edges_from(existing_edges, predicted=False)
    get_missing_edges_for_bt(existing_graph)
