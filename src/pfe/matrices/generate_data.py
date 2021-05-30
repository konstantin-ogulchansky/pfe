import csv
import json
import os
from shutil import copyfile

import networkx as nx
import igraph as ig

from os.path import basename
from pathlib import Path

from pfe.matrices.semiusefull_stuff import get_year_from_filename
from pfe.misc.log import Pretty, Log
from pfe.misc.style import blue, underlined, magenta
from pfe.parse import publications_in
from pfe.tasks.communities import leiden_nx, louvain


# data = Path('test-data/COMP-data')
# graph_path = Path('graph/nice')
# new_data = Path('test-data/COMP-data')


def create_data(graph: nx.Graph, new_data: Path, algorithm: str, publications_till=2018, log_file=Path(''), log=Pretty()):
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
                file.write(f'{algorithm.capitalize()}: {len(publications)} publications.\n')

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


def generate_data_for_algorithms(graph_folders):
    # root_path = Path('test-data/COMP-data/graph/nice')
    # graph_folders = [
    #     # all_years_f := root_path/Path('all_years/float'),
    #     # all_years_i := root_path/Path('all_years/int'),
    #     by_year_i := root_path/Path('by_year/int'),
    #     # by_year_f := root_path/Path('by_year/float'),
    #     # by_year_fs := root_path/Path('by_year/float_selfloop'),
    # ]

    log = Pretty()
    # algorithms = ['leiden', 'louvain']
    algorithms = ['louvain']
    log_file_name = Path('graph.log')

    for algorithm in algorithms:
        for graph_folder in graph_folders:
            for graph_file in graph_folder.iterdir():

                # GraphML
                if graph_file.suffix == '.xml':
                    common_filename = splitext(basename(graph_file))[0]

                    with log.scope.info(f'Creating a folder...'
                                        f'{magenta | common_filename}'):
                        new_subdirectory = graph_folder / common_filename

                        if not os.path.exists(new_subdirectory):
                            new_subdirectory.mkdir()

                    with log.scope.info(f'Reading `GraphML`... {magenta | basename(graph_file).replace("_", " ")}'):
                        graph = nx.read_graphml(graph_file)

                        log.info(f'Read a graph with '
                                 f'{blue | graph.number_of_nodes()} nodes and '
                                 f'{blue | graph.number_of_edges()} edges.')

                        with open(new_subdirectory / log_file_name, 'a+') as log_file:
                            log_file.write(f'{algorithm.capitalize()}: Full graph: {graph.number_of_nodes()} nodes '
                                           f'and {graph.number_of_edges()} edges.\n')

                        largest_component = max(nx.connected_components(graph), key=len)
                        graph = nx.subgraph(graph, largest_component)

                        log.info(f'Subgraph of largest connected component '
                                f'{blue | graph.number_of_nodes()} nodes and '
                                f'{blue | graph.number_of_edges()} edges.')

                        with open(new_subdirectory / log_file_name, 'a+') as log_file:
                            log_file.write(f'{algorithm.capitalize()}: Subgraph, largest component: '
                                           f'{graph.number_of_nodes()} nodes '
                                           f'and {graph.number_of_edges()} edges.\n')

                        with log.scope.info('Generating data...'):
                            year = get_year_from_filename(graph_file)

                            create_data(graph, new_subdirectory, algorithm, year, log_file_name)

                        with log.scope.info('Assign community to a node and update the graph..'):
                            copyfile(graph_file, new_subdirectory/basename(graph_file))
                            graph = nx.read_graphml(new_subdirectory/basename(graph_file))

                            with open(new_subdirectory / f'{algorithm}_author-community.json', 'r') as file:
                                author_community = dict(json.load(file))

                            # graph.remove_nodes_from([node for node in graph.nodes() if node not in author_community.keys()])

                            for author in author_community.keys():
                                graph.nodes[author][f'{algorithm}_community'] = int(author_community[author])

                            nx.write_graphml(graph, new_subdirectory/basename(graph_file))

