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


def louvain(graph: nx.Graph,  data: Path, log: Log):
    """Community detection using the Louvain method."""

    with log.scope.info(f'Detecting communities using the {underlined | "Louvain"} method.'):
        communities = community.best_partition(graph)

    with log.scope.info('Saving communities into a file.'):
        new_communities = {}
        for x, y in communities.items():
            new_communities.setdefault(y, [])
            new_communities[y].append(x)

        with open(data / 'louvain_communities.json', 'w') as file:
            json.dump(new_communities, file)


def leiden(graph: ig.Graph, data: Path, log: Log):
    """Community detection using the Leiden method."""

    odd_vertices = [v.index for v in graph.vs if v.degree() == 2]
    log.info(f'Nodes to delete {len(odd_vertices)}')
    graph.delete_vertices(odd_vertices)

    # graph = (graph.clusters().giant())
    # with open(data / 'ig_giant_cluster.json', 'w') as file:
    #     graph.write_pajek(file)

    with log.scope.info(f'Detecting communities using the {underlined | "Leiden"} method...'):
        objective = 'modularity'
        communities = graph.community_leiden(objective_function=objective, weights='weight')

        log.info('The objective:               ' + objective)
        log.info('The number of communities:   ' + str(blue | len(communities)))
        log.info('The modularity value:        ' + str(blue | communities.modularity))

    with log.scope.info('Saving communities into a file...'):
        with open(data / 'leiden_communities_comp.json', 'w') as file:
            json.dump(dict(enumerate(communities)), file)

    with log.scope.info('Saving the modularity value into a file...'):
        with open(data / 'leiden_modularity_comp.json', 'w') as file:
            json.dump(communities.modularity, file)


if __name__ == '__main__':
    log: Log = Pretty()
    log.info('Starting...')

    ig_data = Path('../../../data/graph/ig')

    with log.scope.info('Reading `ig.Graph`...'):
        ig_graph = ig.Graph.Read_Pajek(str(ig_data / 'ig_comp_graph_relabeled_nodes.net'))

        log.info(f'Read a graph with '
                 f'{blue | len(ig_graph.vs)} vertices and '
                 f'{blue | len(ig_graph.es)} edges.')

    leiden(ig_graph, ig_data, log)

    nx_data = Path('../../../data/graph/nx')

    with log.scope.info('Reading `nx.Graph`.'):
        nx_graph = nx.read_weighted_edgelist(nx_data / 'nx_comp_graph_relabeled_nodes')

        log.info(f'Read a graph with '
                 f'{blue | nx_graph.number_of_nodes()} nodes and '
                 f'{blue | nx_graph.number_of_edges()} edges.')

    louvain(nx_graph, nx_data, log)

