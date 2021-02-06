"""
Saving a renamed graph to a file.
"""

import csv
from pathlib import Path

import networkx as nx

from pfe.misc.log import Pretty
from pfe.parse import parse, all_publications


if __name__ == '__main__':
    log = Pretty()
    log.info('Starting.')

    data = Path('../../../data/graph')

    # Reading a graph.
    if (data / 'nx_full_graph.txt').is_file():
        with log.scope.info('Reading a graph from cache.'):
            graph = nx.read_weighted_edgelist(data / 'nx_full_graph.txt')
    else:
        with log.scope.info('Reading a graph from JSON files.'):
            graph = parse(all_publications(between=(1990, 2018), log=log))

    log.info(f'Read a graph with '
             f'{graph.number_of_nodes()} nodes and '
             f'{graph.number_of_edges()} edges.')

    # Rename nodes and save the graph to a file
    # to be able to read `igraph` faster.
    with log.scope.info('Renaming nodes.'):
        mapping = zip(graph.nodes, range(1, len(graph.nodes)+1))
        mapping = dict(mapping)

        graph = nx.relabel_nodes(graph, mapping, copy=False)

    with log.scope.info('Saving the mapping to a file.'):
        with open(data / 'nx_node_mapping.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(mapping.items())

    # Save the renamed graph to a file.
    with log.scope.info('Saving the nx graph to a file.'):
        nx.write_weighted_edgelist(graph, data / 'nx_graph_relabeled_nodes.txt')

    with log.scope.info('Saving the ig graph to a file.'):
        encoding = 'utf-8'
        with open(data / 'ig_graph_relabeled_nodes.net', 'wb') as f:
            f.write(f'*Vertices {len(graph.nodes())}\n'.encode(encoding))
            f.write('*Edges\n'.encode(encoding))
            nx.write_weighted_edgelist(graph, f, encoding=encoding)



