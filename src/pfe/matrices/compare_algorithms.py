
import json
import os
from os.path import splitext, basename
from pathlib import Path
from shutil import copyfile

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import networkx as nx
import igraph as ig
import numpy as np

from pfe.matrices.by_community_size import plot_cumulative_community_sizes
from pfe.matrices.generate_data import create_data, create_data_igraph
from pfe.matrices.matrix import number_of_communities, log, matrix, to_dataframe, fill_diagonal, \
    add_row_with_community_size, prob_matrix_by_row, prob_matrix_by_all_publications
from pfe.matrices.plot_heatmap import plot_matrix
from pfe.matrices.semiusefull_stuff import get_year_from_filename
from pfe.misc.log import Log, Pretty
from pfe.misc.style import blue, magenta


def difference_matrix(path_to_files: Path):
    # algorithms = ['leiden', 'louvain']
    # for algorithm in algorithms:
    # path_to_files = Path('test-data/COMP-data/graph/nice/by_year/int/nx_comp_nice_1993_int_graph')

    log.info('Reading communities.')
    with open(path_to_files / 'leiden_communities.json', 'r') as file:
        leiden_communities = json.load(file)

    log.info('Reading communities.')
    with open(path_to_files / 'louvain_communities.json', 'r') as file:
        louvain_communities = json.load(file)

    m_communities = len(leiden_communities.keys())
    n_communities = len(louvain_communities.keys())
    matrix = np.zeros(shape=(m_communities, n_communities))

    with log.scope.info('Filling matrix...'):
        for c_leiden in leiden_communities.keys():
            for c_louvain in louvain_communities.keys():
                leiden_members = set(leiden_communities[c_leiden])
                louvain_members = set(louvain_communities[c_louvain])

                diff = len(leiden_members.intersection(louvain_members)) / \
                       len(leiden_members.union(louvain_members))

                matrix[int(c_leiden), int(c_louvain)] = diff

    m = pd.DataFrame(matrix, [str(i) for i in range(m_communities)], [str(i) for i in range(n_communities)])
    plot_matrix(m, 'name', path_to_files,
                title='Similarities between Leiden and Louvain communities',
                xlabel='Louvain',
                ylabel='Leiden',
                prob=True)



def some():
    root_path = Path('test-data/COMP-data/graph/nice')
    graph_folders = [
        # all_years_f := root_path/Path('all_years/float'),
        # all_years_i := root_path/Path('all_years/int'),
        # by_year_i := root_path/Path('by_year/int'),
        by_year_f := root_path/Path('by_year/float'),
        # by_year_fs := root_path/Path('by_year/float_selfloop'),
    ]

    log = Pretty()
    algorithms = ['leiden', 'louvain']
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


if __name__ == '__main__':
    root_path = Path('test-data/COMP-data/graph/nice')
    folders = [
        # all_years_f := root_path/Path('all_years/float'),
        # all_years_i := root_path/Path('all_years/int'),
        by_year_i := root_path/Path('by_year/int'),
        by_year_f := root_path / Path('by_year/float'),
        # by_year_fs := root_path/Path('by_year/float_selfloop'),
    ]

    for graph_folder in folders:
        for subfolder in graph_folder.iterdir():
            if os.path.isdir(subfolder):
                with log.scope.info(f'In {basename(subfolder)}'):
                    difference_matrix(subfolder)

