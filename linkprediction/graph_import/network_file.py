import networkx as nx
import pandas as pd
from werkzeug.datastructures import FileStorage


class NetworkFile:
    def __init__(self, file_format: str, network_file: FileStorage, additional_network_file: FileStorage = None):
        self.file_format = file_format
        self.network_file = network_file
        self.additional_network_file = additional_network_file
        self.network = self.parse_file_to_network()

    def parse_file_to_network(self):
        network = getattr(self, self.file_format)()
        return network

    def parse_nodes(self):
        nodes_list = list(self.network.nodes(data='label'))
        return nodes_list

    def parse_edges(self, nodes):
        # Convert Strings in edges_list to Integers
        edges_list = list(self.network.edges())
        uuid_edges_list: List[tuple] = []
        for edge in edges_list:
            if self.network[edge[0]][edge[1]]['weight'] <= 0.5:
                continue
            edge_tuple: Tuple = ()
            for node in edge:
                edge_tuple = edge_tuple + (dict(nodes).get(int(node)),)
            uuid_edges_list.append(edge_tuple)
        return uuid_edges_list

    def parse_attributes(self, node):
        if self.file_format == 'GML' or self.file_format == 'CSV':
            attribute_list = [(str(k), str(v)) for k, v in self.network.nodes[node].items()]
            return attribute_list
        else:
            attribute_list = [(str(k), str(v)) for k, v in self.network.nodes[str(node)].items()]
            return attribute_list

    def GEXF(self):
        return nx.read_gexf(self.network_file)

    def GraphML(self):
        return nx.read_graphml(self.network_file)

    def GML(self):
        return nx.read_gml(self.network_file, label='id')

    def CSV(self):
        nodes = pd.read_csv(self.network_file.stream, delimiter=';')
        edges = pd.read_csv(self.additional_network_file, delimiter=';')
        G = nx.DiGraph()
        attributes = list(nodes.columns)
        for i in range(len(nodes)):
            G.add_node(nodes.loc[i, "Id"])
            for j in range(len(attributes) - 1):
                node_attribute = {
                    nodes.loc[i, "Id"]:
                        {
                            attributes[j + 1]: nodes.loc[i, attributes[j + 1]],
                        }
                }
                nx.set_node_attributes(G, node_attribute)
        G.update(nx.from_pandas_edgelist(edges, 'source', 'target', True, create_using=nx.DiGraph()))
        return G
