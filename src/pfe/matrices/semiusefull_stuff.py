import json
from os.path import basename
from pathlib import Path

import networkx as nx

from pfe.misc.log import Pretty, Log
from pfe.misc.style import blue
from pfe.parse import publications_in, parse, all_publications


def has_numbers(input):
    return any(char.isdigit() for char in input)


def get_year_from_filename(file: Path):
    year = 0
    if has_numbers(basename(file)):
        year = [int(s) for s in basename(file).split('_') if s.isdigit()][0]

    return year


def get_mapping(file: Path, graph_folder: Path):
    if has_numbers(basename(file)):
        year = [int(s) for s in basename(file).split('_') if s.isdigit()][0]

        for graph_file in graph_folder.iterdir():
            if graph_file.suffix == '.csv' and str(year) in basename(graph_file):
                return graph_file

    else:
        for graph_file in graph_folder.iterdir():
            if graph_file.suffix == '.csv':
                return graph_file


def show_number_of_publications_among_1_2_3and_more_communities():
    log: Log = Pretty()
    log.info('Starting...')

    data = Path('../../../data/graph/ig')
    test_stuff = Path('test-data/COMP-data/graph/nice/by_year/int/nx_comp_nice_2018_int_graph')

    with log.scope.info('Reading authors-communities...'):
        with open(test_stuff / 'stats_largest_cluster_leiden.json', 'r') as file:
            stats = json.load(file)

    n = 0
    one_comm = 0
    two_comm = 0
    all_other_comm = 0
    z = 0
    with log.scope.info('Counting publications by number of communities...'):
        for s in stats:
            s.pop('publication_id')
            if len(s) == 1:
                one_comm += 1
            elif len(s) == 2:
                two_comm += 1
            elif len(s) >= 3:
                all_other_comm += 1
            elif len(s) < 1:
                z += 1
            n += 1

    log.info(f'Publications in: ')
    log.info(f'1 community: {blue | one_comm} ')
    log.info(f'2 communities: {blue | two_comm} ')
    log.info(f'all other: {blue | all_other_comm} ')
    log.info(f'Total: {blue | n} ')

    print(z)
    print(n - z)
    print(one_comm + two_comm + all_other_comm)
    print()
    print(one_comm / (n - z))
    print(two_comm / (n - z))
    print(all_other_comm / (n - z))


def generate_graphs_by_year():
    '''
    generates graphs(GraphML) that consists of publications
    between 1990 and 'year'
    '''

    path = Path('matrices/test-data/All-disc')

    log = Pretty()
    with log.scope.info('Starting.'):
        # for year in range(2013, 2016):
        #
        #     graph = parse(all_publications(between=(1990, year), log=log))
        #     nx.write_graphml(graph, path / Path(f'nx_int_graph_{year}.xml'))

        for year in range(1990, 2018 +1):

            with log.scope.info('Reading a graph.'):
                graph = parse(all_publications(between=(1990, year), log=log), self_loops=False)

                log.info(f'Read a graph with '
                         f'{blue | graph.number_of_nodes()} nodes and '
                         f'{blue | graph.number_of_edges()} edges.')

                with open(path / 'graph.log', 'a+') as log_file:
                    log_file.write(f'Graph {1990, year}: '
                                   f'{graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges.\n')

            nx.write_graphml(graph, path / Path(f'nx_full_{year}_int_graph.xml'))