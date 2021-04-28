import csv
import json
from pathlib import Path
import igraph as ig
from pfe.misc.log import Pretty, Log
from pfe.misc.style import blue, underlined
from pfe.parse import publications_in
import networkx as nx


# data = Path('test-data/COMP-data')
# graph_path = Path('graph/nice')
# new_data = Path('test-data/COMP-data')
from pfe.tasks.communities import leiden_nx, louvain


# def create_data_igraph(graph: ig.Graph, mapping_path: Path,  new_data: Path, log=Pretty()):
def create_data_igraph(graph: ig.Graph, new_data: Path, log=Pretty()):

    # with log.scope.info('Reading `ig.Graph`...'):
    #     # graph = ig.Graph.Read_Pajek(str(data / 'ig_full_graph_relabeled_nodes.net'))
    #     graph = ig.Graph.Read_Pajek(str(data / graph_path / 'ig_comp_nice_all_int_graph.net'))
    #
    #     log.info(f'Read a graph with '
    #              f'{blue | len(graph.vs)} vertices and '
    #              f'{blue | len(graph.es)} edges.')
    #
    # graph = graph.clusters().giant()
    #
    # log.info(f'Subgraph with '
    #          f'{blue | len(graph.vs)} vertices and '
    #          f'{blue | len(graph.es)} edges.')

    with log.scope.info(f'Detecting communities using the {underlined | "ig Leiden"} method...'):
        objective = 'modularity'
        communities = graph.community_leiden(weights='weight', objective_function=objective)

        log.info('The objective:               ' + objective)
        log.info('The number of communities:   ' + str(blue | len(communities)))
        log.info('The modularity value:        ' + str(blue | communities.modularity))

    with log.scope.info('Saving the modularity value into a file...'):
        with open(new_data / 'ig_leiden_modularity.json', 'w') as file:
            json.dump(communities.modularity, file)

    # skip communities with 1 member
    communities = [c for c in communities if len(c) > 1]

    with log.scope.info('Saving communities into a file...'):
        with open(new_data / 'ig_leiden_communities.json', 'w') as file:
            json.dump(dict(enumerate(communities)), file)

    return

    communities = dict(enumerate(communities))
    new_dict = {}

    for k_community, v_authors in communities.items():
        for author in v_authors:
            new_dict[int(author)] = k_community

    communities = new_dict

    with log.scope.info('Saving author-community into a file...'):
        with open(new_data / 'leiden_author-community.json', 'w') as file:
            json.dump(communities, file)

    with log.scope.info('Reading authors-communities.'):
        with open(new_data / 'leiden_author-community.json', 'r') as file:
            communities = json.load(file)

    mapping = {}
    # with open(data / 'nx_node_mapping.csv', 'r') as file:
    # with open(data/ graph_path / 'nx_node_mapping_nice_all_int.csv', 'r') as file:
    with open(mapping_path, 'r') as file:

        reader = csv.reader(file)
        for row in reader:
            mapping[row[0]] = int(row[1])

    publication_counter = 0
    node_list = [x.index for x in graph.vs]

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
                # log.info(f'id {id}, mapping[id] {mapping[id]}')
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


def create_data_cdlib_relabeled_graph(graph: nx.Graph,  mapping_path: Path,  new_data: Path, publications_till=2018, log_file=''):
    log: Log = Pretty()

    leiden_nx(graph, new_data, log)

    log.info('Reading communities.')
    with open(new_data / 'leiden_communities.json', 'r') as file:
            communities = json.load(file)

    new_dict = {}

    for k_community, v_authors in communities.items():
        for author in v_authors:
            new_dict[str(author)] = int(k_community)

    communities = new_dict

    log.info('Saving author-community into a file...')
    with open(new_data / 'leiden_author-community.json', 'w') as file:
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

        publications = list(publications_in('COMP', between=(1990, publications_till)))
        log.info(f'{blue | len(publications)} publications.')

        if log_file != '':
            with open(new_data / log_file, 'a+') as file:
                file.write(f'{len(publications)} publications.')

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

    log.info('Saving statistics into a file...')
    with open(new_data / 'stats_largest_cluster.json', 'w') as file:
        json.dump(stats, file)


def create_data(graph: nx.Graph, new_data: Path, algorithm: str, publications_till=2018, log_file='', log=Pretty()):
    if algorithm == 'leiden':
        leiden_nx(graph, new_data, log)
    elif algorithm == 'louvain':
        louvain(graph, new_data, log)
    else:
        m = f'Wrong name of the algorithm.\n'\
            f'Got {algorithm}, expected \'leiden\' or \'louvain\''
        log.error(m)
        raise Exception(m)


    log.info('Reading communities.')
    with open(new_data / f'{algorithm}_communities.json', 'r') as file:
            communities = json.load(file)

    new_dict = {}

    for k_community, v_authors in communities.items():
        for author in v_authors:
            new_dict[str(author)] = int(k_community)

    communities = new_dict

    log.info('Saving author-community into a file...')
    with open(new_data / f'{algorithm}_author-community.json', 'w') as file:
        json.dump(communities, file)

    node_list = [int(x) for x in graph.nodes()]

    with log.scope.info('Delete graph...'):
        del graph

    publication_counter = 0
    with log.scope.info('Collecting statistics...'):

        if publications_till == 0:
            publications_till = 2018

        publications = list(publications_in('COMP', between=(1990, publications_till)))
        log.info(f'{blue | len(publications)} publications.')

        if log_file != '':
            with open(new_data / log_file, 'a+') as file:
                file.write(f'{algorithm.capitalize()}: {len(publications)} publications.')

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
                if int(id) not in node_list:
                    all = False

            if all:
                for author in authors:
                    if str(author) in communities.keys():
                        community = f'community {communities[str(author)]}'

                        if community in statistics.keys():
                            statistics[community] += 1
                        else:
                            statistics[community] = 1

            # if publication_counter % 500 == 0:
            #     log.info(f'{blue | publication_counter} ...')

            stats.append(statistics)

    log.info('Saving statistics into a file...')
    with open(new_data / f'stats_largest_cluster_{algorithm}.json', 'w') as file:
        json.dump(stats, file)