"""
Community detection.
"""

import json
from pathlib import Path

import community
import networkx as nx
import igraph as ig

from pfe.misc.style import blue, underlined
from pfe.misc.log import Log, Pretty


def louvain(data: Path, log: Log):
    """Community detection using the Louvain method."""

    with log.scope.info('Reading `nx.Graph`.'):
        graph = nx.read_weighted_edgelist(data / 'nx_full_graph_relabeled_nodes.txt')

        log.info(f'Read a graph with '
                 f'{blue | graph.number_of_nodes()} nodes and '
                 f'{blue | graph.number_of_edges()} edges.')

    with log.scope.info(f'Detecting communities using the {underlined | "Louvain"} method.'):
        communities = community.best_partition(graph)

    with log.scope.info('Saving communities into a file.'):
        new_communities = {}
        for x, y in communities.items():
            new_communities.setdefault(y, [])
            new_communities[y].append(x)

        with open(data / 'louvain_communities.json', 'w') as file:
            json.dump(new_communities, file)


def leiden(data: Path, log: Log):
    """Community detection using the Leiden method."""

    with log.scope.info('Reading `ig.Graph`...'):
        graph = ig.Graph.Read_Pajek(str(data / 'ig_full_graph_relabeled_nodes.net'))

        log.info(f'Read a graph with '
                 f'{blue | len(graph.vs)} vertices and '
                 f'{blue | len(graph.es)} edges.')

    with log.scope.info(f'Detecting communities using the {underlined | "Leiden"} method...'):
        objective = 'modularity'
        communities = graph.community_leiden(objective_function=objective, weights='weight')

        log.info('The objective:               ' + objective)
        log.info('The number of communities:   ' + str(blue | len(communities)))
        log.info('The modularity value:        ' + str(blue | communities.modularity))

    with log.scope.info('Saving communities into a file...'):
        with open(data / 'leiden_communities.json', 'w') as file:
            json.dump(dict(enumerate(communities)), file)

    with log.scope.info('Saving the modularity value into a file...'):
        with open(data / 'leiden_modularity.json', 'w') as file:
            json.dump(communities.modularity, file)


if __name__ == '__main__':
    log: Log = Pretty()
    log.info('Starting...')

    data = Path('../../../data/graph')

    # louvain(data / 'nx', log)
    leiden(data / 'ig', log)
