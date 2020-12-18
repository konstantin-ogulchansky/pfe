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
    log.info('Starting...')

    data = Path('../../data/graph')

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
        mapping = zip(graph.nodes, range(len(graph.nodes)))
        mapping = dict(mapping)

        graph = nx.relabel_nodes(graph, mapping, copy=False)

    # Save the renamed graph to a file.
    with log.scope.info('Saving the graph to a file.'):
        with open(data / 'nx_node_mapping.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(mapping.items())

        nx.write_weighted_edgelist(graph, data / 'nx_full_graph_relabeled_nodes.txt')
