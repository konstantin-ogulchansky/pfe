"""
Community detection.
"""

import json
from collections import Counter

import community as louvain
import networkx as nx


def save(communities: dict, path: str):
    """Saves the sizes of `communities` to a file.

    :param communities: a dictionary that maps each member of a network
                        (i.e., each node) to their community.
    :param path: a path to a file to save community sizes to.
    """

    with open(path, 'w') as file:
        json.dump(Counter(communities.values()), file)


if __name__ == '__main__':
    from pfe.misc.log import timestamped, cx

    log = timestamped
    log('Starting...')

    with cx(log, 'Reading a graph...'):
        graph = nx.read_weighted_edgelist('../../nx_full_graph_relabeled_nodes.txt')

    log(f'Read a graph with '
        f'{graph.number_of_nodes()} nodes and '
        f'{graph.number_of_edges()} edges.')

    # Detect communities using the Louvain method.
    with cx(log, 'Detecting communities using the Louvain method...'):
        communities = louvain.best_partition(graph)

    # Save detected communities to a file.
    with cx(log, 'Saving communities to a file...'):
        save(communities, 'components_nx_full_graph.json')
