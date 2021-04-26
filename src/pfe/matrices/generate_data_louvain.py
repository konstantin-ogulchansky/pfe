import csv
import json
from pathlib import Path
import igraph as ig
import networkx as nx
from pfe.misc.log import Pretty, Log
from pfe.misc.style import blue, underlined
from pfe.parse import publications_in
from pfe.tasks.communities import louvain

# data = Path('test-data/COMP-data')
# new_data = Path('test-data/COMP-data')


def create_data_louvain(graph: nx.Graph, mapping_path: Path,  new_data: Path):
    log: Log = Pretty()


    # with log.scope.info('Reading `nx.Graph`.'):
    #     graph = nx.read_weighted_edgelist(data / 'nx_comp_graph_relabeled_nodes.txt')
    #     # graph = nx.read_edgelist(data / 'nx_comp_graph_relabeled_nodes.txt', data=False)
    #
    #     log.info(f'Read a graph with '
    #              f'{blue | graph.number_of_nodes()} nodes and '
    #              f'{blue | graph.number_of_edges()} edges.')
    #
    #     largest_component = max(nx.connected_components(graph), key=len)
    #     graph = nx.subgraph(graph, largest_component)
    #
    #     log.info(f'Subgraph of largest connected component '
    #              f'{blue | graph.number_of_nodes()} nodes and '
    #              f'{blue | graph.number_of_edges()} edges.')

    louvain(graph, new_data, log)

    with log.scope.info('Reading communities.'):
        with open(new_data / 'louvain_communities.json', 'r') as file:
            communities = json.load(file)

    new_dict = {}

    for k_community, v_authors in communities.items():
        for author in v_authors:
            new_dict[str(author)] = int(k_community)

    communities = new_dict

    with log.scope.info('Saving author-community into a file...'):
        with open(new_data / 'louvain_author-community.json', 'w') as file:
            json.dump(communities, file)

    mapping = {}
    with open(mapping_path, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            mapping[row[0]] = int(row[1])

    publication_counter = 0
    node_list = [int(x) for x in graph.nodes()]

    with open(new_data / 'node_list.txt', 'w') as file:
        file.write(str(node_list))

    with open(new_data / 'mapping.txt', 'w') as file:
        file.write(str(mapping))

    with log.scope.info('Delete graph...'):
        del graph

    with log.scope.info('Collecting statistics...'):

        publications = list(publications_in('COMP', between=(1990, 2018)))
        log.info(f'{blue | len(publications)} publications.')

        stats = []
        for publication in publications:

            publication_counter += 1

            authors = []
            for author in publication['authors']:
                authors.append(author['id'])

            # statistics = {}
            statistics = {'publication_id': publication['id']}

            all = True
            for id in authors:
                # log.info(f'id {id}, mapping[id] {mapping[id]  if id in mapping.keys() else 0}')
                if id not in mapping.keys():
                    all = False
                elif mapping[id] not in node_list:
                    all = False

            if all:
                for author in authors:
                    if str(mapping[author]) in communities.keys():
                        community = f'community {communities[str(mapping[author])]}'

                        if community in statistics.keys():
                            statistics[community] += 1
                        else:
                            statistics[community] = 1

            # if publication_counter % 500 == 0:
            #     log.info(f'{blue | publication_counter} ...')

            stats.append(statistics)

    with log.scope.info('Saving statistics into a file...'):
        with open(new_data / 'stats_largest_cluster.json', 'w') as file:
            json.dump(stats, file)

