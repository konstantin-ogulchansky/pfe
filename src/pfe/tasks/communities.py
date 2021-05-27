"""
Community detection.
"""

import json
from pathlib import Path

import community
import networkx as nx
import igraph as ig
from cdlib import algorithms

from pfe.misc.style import blue, underlined
from pfe.misc.log import Log, Pretty, Nothing


def louvain(graph: nx.Graph,  data: Path, log: Log = Nothing()):
    """Community detection using the Louvain method."""

    # odd_vertices = [v for v in graph.nodes if graph.degree[v] == 2]
    # log.info(f'Nodes to delete {len(odd_vertices)}')
    #
    # graph.remove_nodes_from(odd_vertices)

    for e in graph.edges:
        graph.edges[e]['weight'] = float(graph.edges[e]['weight'])

    # graph = max(nx.connected_components(graph), key=len)

    with log.scope.info(f'Detecting communities using the {underlined | "Louvain"} method.'):
        communities = community.best_partition(graph, weight='weight')


    with log.scope.info('Saving communities into a file.'):
        new_communities = {}
        for x, y in communities.items():
            new_communities.setdefault(y, [])
            new_communities[y].append(int(x))

        new_communities = new_communities.values()
        sorted(new_communities, key=len, reverse=True)

        with open(data / 'louvain_communities.json', 'w') as file:
            json.dump(dict(enumerate(new_communities)), file)

        modularity = community.modularity(communities, graph)
        with log.scope.info('Saving the modularity value into a file...'):
            with open(data / 'louvain_modularity_comp.json', 'w') as file:
                json.dump(modularity, file)

        with open(data / 'graph.log', 'a+') as file:
            file.write(f'Leiden: {modularity}\n')


def leiden(graph: ig.Graph, data: Path, log: Log = Nothing()):
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

    sorted(communities, key=len, reverse=True)

    with log.scope.info('Saving communities into a file...'):
        with open(data / 'leiden_communities_full.json', 'w') as file:
            json.dump(dict(enumerate(communities)), file)

    with log.scope.info('Saving the modularity value into a file...'):
        with open(data / 'leiden_modularity_full.json', 'w') as file:
            json.dump(communities.modularity, file)

    with open(data / 'graph.log', 'a+') as file:
        file.write(f'Leiden: {communities.modularity}\n')


def leiden_nx(graph: nx.Graph,  data: Path, log: Log = Nothing()):
    """Community detection using the Leiden method from cdlib."""

    # odd_vertices = [v for v in graph.nodes if graph.degree[v] == 2]
    # log.info(f'Nodes to delete {len(odd_vertices)}')
    #
    # graph.remove_nodes_from(odd_vertices)
    #
    # for e in graph.edges:
    #     graph.edges[e]['weight'] = float(graph.edges[e]['weight'])

    with log.scope.info(f'Detecting communities using the {underlined | "Leiden"} method.'):
        communities = algorithms.leiden(graph)

    modularity = {
        'modularity_density': communities.modularity_density().score,
        'erdos_renyi_modularity': communities.erdos_renyi_modularity(),
        'newman_girvan_modularity': communities.newman_girvan_modularity(),
        'z_modularity': communities.z_modularity()
    }

    comm = []
    for c in communities.communities:
        if len(c) > 1:
            comm.append([int(i) for i in c])
    communities = comm
    sorted(communities, key=len, reverse=True)

    with log.scope.info('Saving communities into a file...'):
        with open(data / 'leiden_communities.json', 'w') as file:
            json.dump(dict(enumerate(communities)), file)

        # with open(data / 'louvain_communities.json', 'w') as file:
        #     json.dump(new_communities, file)
        #
    with log.scope.info('Saving the modularity value into a file...'):
        with open(data / 'leiden_cdlib_modularity.json', 'w') as file:
            json.dump(modularity, file)

    with open(data / 'graph.log', 'a+') as file:
        file.write(f'Leiden: {modularity["newman_girvan_modularity"]}\n')


if __name__ == '__main__':
    log: Log = Pretty()
    log.info('Starting...')

    ig_data = Path('../../../data/graph/ig')
    #
    # with log.scope.info('Reading `ig.Graph`...'):
    #     ig_graph = ig.Graph.Read_Pajek(str(ig_data / 'ig_comp_graph_relabeled_nodes.net'))
    #
    #     log.info(f'Read a graph with '
    #              f'{blue | len(ig_graph.vs)} vertices and '
    #              f'{blue | len(ig_graph.es)} edges.')

    # leiden(ig_graph, ig_data, log)

    nx_data = Path('../../../data/graph/nx')

    with log.scope.info('Reading `nx.Graph`.'):
        nx_graph = nx.read_weighted_edgelist(nx_data / 'nx_comp_graph_relabeled_nodes')

        log.info(f'Read a graph with '
                 f'{blue | nx_graph.number_of_nodes()} nodes and '
                 f'{blue | nx_graph.number_of_edges()} edges.')

    leiden_nx(nx_graph, nx_data, log)