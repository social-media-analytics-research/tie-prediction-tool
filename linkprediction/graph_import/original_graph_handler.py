import networkx as nx
from networkx import DiGraph

from linkprediction.database_connector import DatabaseConnector

COLOR_ORIGINAL_ONLY = '#133F5C'


def build_original_graph(id_type, reference_id, return_type='hierarchical'):
    """
    id_type: possible values = ['original_network_id', 'project_id']
    reference_id: value of the id
    return_type:
        hierarchical -> returns original_graph_hierarchical
        flat -> returns original_graph_flat
        both -> returns (original_graph_hierarchical, original_graph_flat)
    """
    if id_type not in ['original_network_id', 'project_id']:
        raise ValueError('Parameter id_type is not valid!')
    if return_type not in ['hierarchical', 'flat', 'both']:
        raise ValueError('Parameter return_type is not valid!')
    try:
        db = DatabaseConnector.get_db_instance()
        nodes = db.get_nodes_by_id(id_type, reference_id)
        uuid_to_id = {node['node_id']: node['node_network_id'] for node in nodes}
        edges = db.get_edges_of_original_network_by_id(id_type, reference_id)
        edges_flat = edges.copy()
        edges_hierarchical = edges.copy()
        original_graph_flat = DiGraph()
        original_graph_hierarchical = DiGraph()

        for node in nodes:
            if return_type == 'hierarchical' or return_type == 'both':
                node_attributes = db.get_node_attributes_by_id('node_id', node['node_id'])
                kv_attributes = {
                    record['attribute_name']: record['attribute_value'] for record in node_attributes
                }
                original_graph_hierarchical.add_node(
                    node_for_adding=node['node_network_id'],
                    identifiers={**node},
                    **kv_attributes
                )
            if return_type == 'flat' or return_type == 'both':
                original_graph_flat.add_node(
                    node_for_adding=node['node_network_id']
                )

        if return_type == 'hierarchical' or return_type == 'both':
            for edge in edges_hierarchical:
                source_node_record = next(filter(lambda x: x['node_id'] == edge['source_node'], nodes))
                target_node_record = next(filter(lambda x: x['node_id'] == edge['target_node'], nodes))
                sub_edges = [{
                    'source': source_node_record['node_network_id'],
                    'target': target_node_record['node_network_id'],
                    'predicted': False
                }]
                rev_edge = next(filter(lambda x: x['target_node'] == edge['source_node']
                                and x['source_node'] == edge['target_node'], edges), None)
                if rev_edge is not None:
                    sub_edges.append(
                        {
                            'source': target_node_record['node_network_id'],
                            'target': source_node_record['node_network_id'],
                            'predicted': False
                        }
                    )
                    edges_hierarchical.remove(rev_edge)

                edge[uuid_to_id[edge['source_node']]] = edge['source_node']
                edge[uuid_to_id[edge['target_node']]] = edge['target_node']

                original_graph_hierarchical.add_edge(
                    u_of_edge=source_node_record['node_network_id'],
                    v_of_edge=target_node_record['node_network_id'],
                    identifiers={**edge},
                    edges=sub_edges,
                    edge_color=COLOR_ORIGINAL_ONLY
                )

        if return_type == 'flat' or return_type == 'both':
            for edge in edges_flat:
                source_node_record = next(
                    filter(lambda x: x['node_id'] == edge['source_node'], nodes))
                target_node_record = next(
                    filter(lambda x: x['node_id'] == edge['target_node'], nodes))

                edge[uuid_to_id[edge['source_node']]] = edge['source_node']
                edge[uuid_to_id[edge['target_node']]] = edge['target_node']

                original_graph_flat.add_edge(
                    u_of_edge=source_node_record['node_network_id'],
                    v_of_edge=target_node_record['node_network_id'],
                    identifiers={**edge},
                    edge_color=COLOR_ORIGINAL_ONLY,
                    predicted=False
                )

        if return_type == 'flat':
            return original_graph_flat
        if return_type == 'hierarchical':
            return original_graph_hierarchical
        if return_type == 'both':
            return (original_graph_hierarchical, original_graph_flat)
    except Exception as error:
        print(error)
        return ('Exception', error)
