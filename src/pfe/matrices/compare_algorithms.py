import csv
import json
import os
from operator import itemgetter
from os.path import splitext, basename
from pathlib import Path
from shutil import copyfile

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import networkx as nx
import igraph as ig
import numpy as np

from pfe.matrices.generate_data import create_data
from pfe.matrices.matrix import  sort_matrix
from pfe.matrices.plot_heatmap import plot_matrix
from pfe.matrices.semiusefull_stuff import get_year_from_filename, get_mapping
from pfe.misc.log import Pretty
from pfe.misc.style import blue, magenta


def jaccard(x: set, y: set):
    return len(x.intersection(y))/len(x.union(y))


def difference_matrix_collaborations(algorithm: str, nice_2018: Path, graph_2018: Path, _from=2013):
        '''
        For each pair of years
        For a pair of algorithms

        take network 2018
        keep nodes from 'year'

        take all edges inside community 'A' and make set
        take network 'year'
        take all edges inside community '1' and make set

        make jaccard matrix
        '''

        log.info(f'Reading communities {2018}.')
        graph = nx.read_graphml(graph_2018)

        # to keep only needed nodes
        # nx.subgraph(graph, subset).copy()

        with open(nice_2018 / f'{algorithm}_communities.json', 'r') as file:
            communities_2018 = json.load(file)

        for year in range(_from, 2018):
            nice_year = Path(f'test-data/COMP-data/graph/nice/by_year/int/nx_comp_nice_{year}_int_graph')
            graph_year = nx.read_graphml(f'test-data/COMP-data/graph/nice/by_year/int/nx_comp_nice_{year}_int_graph.xml')

            log.info(f'Reading communities {year}.')
            with open(nice_year / f'{algorithm}_communities.json', 'r') as file:
                communities_year = json.load(file)

            with open(nice_year / f'{algorithm}_author-community.json', 'r') as file:
                authors_year = dict(json.load(file))

            authors_year = set([int(k) for k in authors_year.keys()])

            m_communities = len(communities_2018.keys())
            n_communities = len(communities_year.keys())
            matrix = np.zeros(shape=(m_communities, n_communities))

            with log.scope.info('Filling matrix...'):
                for c_18 in communities_2018.keys():
                    for c_year in communities_year.keys():
                        members_18 = set(communities_2018[c_18]).intersection(authors_year)
                        members_year = set(communities_year[c_year])

                        edges_2018 = nx.subgraph(graph, [str(m) for m in members_18]).copy()
                        edges_2018 = [tuple(sorted([int(u), int(v)])) for u, v in edges_2018.edges]

                        edges_year = nx.subgraph(graph_year, [str(m) for m in members_year]).copy()
                        edges_year = [tuple(sorted([int(u), int(v)])) for u, v in edges_year.edges]

                        diff = jaccard(set(edges_2018), set(edges_year))

                        matrix[int(c_18), int(c_year)] = diff

            np.savetxt(nice_year / f'mtr_similarities_{algorithm}_18_{year - 2000}_collaborations.csv', matrix, fmt='%.4f')

            m = pd.DataFrame(matrix, [str(i) for i in range(m_communities)], [str(i) for i in range(n_communities)])
            m = sort_matrix(m)

            plot_matrix(m, f'similarities_{algorithm}_18_{year - 2000}_collaborations', nice_year,
                        title=f'Similarities between {algorithm} 2018-{year}\nCollaborations',
                        subtitle=f'{len(communities_2018)} communities in 2018 & {len(communities_year)} communities in {year}',
                        xlabel=f'{year}',
                        ylabel='2018',
                        prob=True)


def difference_matrix_by_year_members(algorithm: str, nice_2018: Path, _from=2013):
    # algorithm = 'louvain'

    # nice_2018 = Path('test-data/COMP-data/graph/nice/by_year/int/nx_comp_nice_2018_int_graph')

    log.info(f'Reading communities {2018}.')
    with open(nice_2018 / f'{algorithm}_communities.json', 'r') as file:
        communities_2018 = json.load(file)

    print('2018 communities:', len(communities_2018
                                   ))

    for year in range(_from, 2018):
        nice_year = Path(f'test-data/COMP-data/graph/nice/by_year/int/nx_comp_nice_{year}_int_graph')

        log.info(f'Reading communities {year}.')
        with open(nice_year / f'{algorithm}_communities.json', 'r') as file:
            communities_year = json.load(file)

        with open(nice_year / f'{algorithm}_author-community.json', 'r') as file:
            authors_year = dict(json.load(file))

        authors_year = set([int(k) for k in authors_year.keys()])

        m_communities = len(communities_2018.keys())
        n_communities = len(communities_year.keys())
        matrix = np.zeros(shape=(m_communities, n_communities))

        with log.scope.info('Filling matrix...'):
            for c_18 in communities_2018.keys():
                for c_year in communities_year.keys():
                    members_18 = set(communities_2018[c_18]).intersection(authors_year)
                    members_year = set(communities_year[c_year])

                    diff = len(members_year.intersection(members_18))/len(members_year)

                    matrix[int(c_18), int(c_year)] = diff

        np.savetxt(nice_year / f'mtr_similarities_{algorithm}_18_{year - 2000}_per_members.csv', matrix, fmt='%.4f')
        m = pd.DataFrame(matrix, [str(i) for i in range(m_communities)], [str(i) for i in range(n_communities)])

        print(year, ' communities', len(communities_year))
        m, best_matching = sort_matrix(m, year=year)

        all_authors = sum(len(communities_year[c]) for c in communities_year.keys())

        some = []
        stayed = 0
        total = 0
        for c_year, c_18, _ in best_matching:
            c_18 = str(c_18)
            c_year = str(c_year)
            members_18 = set(communities_2018[c_18])
            members_year = set(communities_year[c_year])

            members_stayed_in = len(members_year.intersection(members_18))
            some.append({
                'year': year,
                'from_community': c_year,
                'in_community': c_18,
                'stayed': members_stayed_in,
                'total': len(members_year)
            })

            total += len(members_year)
            stayed += members_stayed_in

        print('Total in community: ', total)
        print('Stayed: ', stayed)

        some.insert(0, {'all_authors': all_authors, 'stayed': stayed, 'part': stayed/all_authors})


        with open(nice_year/f'{algorithm}_stability_thing.json', 'w+') as file:
            json.dump(some, file)


        # plot_matrix(m, f'similarities_{algorithm}_18_{year-2000}_per_members', nice_year,
        #             title=f'Similarities between {algorithm} 2018-{year}\n'
        #                   f'|Members({year}) ∩ Members(2018)|/'
        #                   f'|Members({year})|',
        #             subtitle=f'{len(communities_2018)} communities in 2018 & {len(communities_year)} communities in {year}',
        #             xlabel=f'{year}',
        #             ylabel='2018',
        #             prob=True)

        m = m.transpose()
        # m = pd.DataFrame(matrix, [str(i) for i in range(n_communities)], [str(i) for i in range(m_communities)])

        # plot_matrix(m, f'transposed_similarities_{algorithm}_18_{year-2000}_per_members', nice_year,
        #             title=f'Similarities between {algorithm} 2018-{year}\n'
        #                   f'Transposed\n'
        #                   f'|Members({year}) ∩ Members(2018)|/'
        #                   f'|Members({year})|',
        #             subtitle=f'{len(communities_2018)} communities in 2018 & {len(communities_year)} communities in {year}',
        #             ylabel=f'{year}',
        #             xlabel='2018',
        #             prob=True)


def difference_matrix_by_year_members_jaccard(algorithm: str, nice_2018: Path, _from=2013):
    # algorithm = 'louvain'

    # nice_2018 = Path('test-data/COMP-data/graph/nice/by_year/int/nx_comp_nice_2018_int_graph')

    log.info(f'Reading communities {2018}.')
    with open(nice_2018 / f'{algorithm}_communities.json', 'r') as file:
        communities_2018 = json.load(file)

    for year in range(_from, 2018):
        nice_year = Path(f'test-data/COMP-data/graph/nice/by_year/int/nx_comp_nice_{year}_int_graph')

        log.info(f'Reading communities {year}.')
        with open(nice_year / f'{algorithm}_communities.json', 'r') as file:
            communities_year = json.load(file)

        with open(nice_year / f'{algorithm}_author-community.json', 'r') as file:
            authors_year = dict(json.load(file))

        authors_year = set([int(k) for k in authors_year.keys()])

        m_communities = len(communities_2018.keys())
        n_communities = len(communities_year.keys())
        matrix = np.zeros(shape=(m_communities, n_communities))

        with log.scope.info('Filling matrix...'):
            for c_18 in communities_2018.keys():
                for c_year in communities_year.keys():
                    members_18 = set(communities_2018[c_18]).intersection(authors_year)
                    members_year = set(communities_year[c_year])

                    diff = jaccard(members_year, members_18)

                    matrix[int(c_18), int(c_year)] = diff

        np.savetxt(nice_year / f'mtr_similarities_{algorithm}_18_{year-2000}_jac_members.csv', matrix, fmt='%.4f')

        m = pd.DataFrame(matrix, [str(i) for i in range(m_communities)], [str(i) for i in range(n_communities)])
        m = sort_matrix(m)

        plot_matrix(m, f'similarities_{algorithm}_18_{year-2000}_jac_members', nice_year,
                    title=f'Similarities between {algorithm} 2018-{year}\nJaccard index by members of 2 communities',
                    subtitle=f'{len(communities_2018)} communities in 2018 & {len(communities_year)} communities in {year}',
                    xlabel=f'{year}',
                    ylabel='2018',
                    prob=True)


def difference_matrix_leidens(path_to_files: Path):
    # algorithms = ['leiden', 'louvain']
    # for algorithm in algorithms:
    # path_to_files = Path('test-data/COMP-data/graph/nice/by_year/int/nx_comp_nice_1993_int_graph')

    log.info('Reading communities.')
    with open(path_to_files / 'leiden_communities.json', 'r') as file:
        leiden_communities = json.load(file)

    log.info('Reading communities.')
    with open(path_to_files / 'ig_leiden_communities.json', 'r') as file:
        louvain_communities = json.load(file)

    m_communities = len(leiden_communities.keys())
    n_communities = len(louvain_communities.keys())
    matrix = np.zeros(shape=(m_communities, n_communities))

    with log.scope.info('Filling matrix...'):
        for c_leiden in leiden_communities.keys():
            for c_louvain in louvain_communities.keys():
                leiden_members = set(leiden_communities[c_leiden])
                mapping = {}
                with open(get_mapping(path_to_files, path_to_files), 'r') as file:
                    reader = csv.reader(file)
                    for row in reader:
                        mapping[int(row[1])] = int(row[0])

                louvain_members = set([mapping[i] for i in louvain_communities[c_louvain] if i != 0])

                # diff = jaccard(leiden_members, louvain_members)
                diff = len(leiden_members.intersection(louvain_members)) / len(leiden_members)

                matrix[int(c_leiden), int(c_louvain)] = diff

    np.savetxt(path_to_files / f'mtr_similarities_leiden_ig_cdlib_per.csv', matrix, fmt='%.4f')

    m = pd.DataFrame(matrix, [str(i) for i in range(m_communities)], [str(i) for i in range(n_communities)])
    m = sort_matrix(m)

    plot_matrix(m, 'similarities_leiden_ig_cdlib_per', path_to_files,
                title='Similarities between Leiden(cdlib) and Leiden(ig) communities',
                xlabel='Leiden(ig)',
                ylabel='Leiden(cdlib)',
                prob=True)


def difference_matrix_leiden_louvain(path_to_files: Path):
    # algorithms = ['leiden', 'louvain']
    # for algorithm in algorithms:
    # path_to_files = Path('test-data/COMP-data/graph/nice/by_year/int/nx_comp_nice_1993_int_graph')

    # for graph_folder in folders:
    #     for subfolder in graph_folder.iterdir():
    #         if os.path.isdir(subfolder):
    #             with log.scope.info(f'In {basename(subfolder)}'):
    #                 difference_matrix_leiden_louvain(subfolder)

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

                # diff = jaccard(leiden_members, louvain_members)
                diff = len(leiden_members.intersection(louvain_members)) / len(leiden_members)

                matrix[int(c_leiden), int(c_louvain)] = diff

    np.savetxt(path_to_files / f'similarities_leiden_louvain_per.csv', matrix, fmt='%.4f')

    m = pd.DataFrame(matrix, [str(i) for i in range(m_communities)], [str(i) for i in range(n_communities)])
    m = sort_matrix(m)

    plot_matrix(m, 'similarities_leiden_louvain_per', path_to_files,
                title='Similarities between Leiden and Louvain communities',
                xlabel='Louvain',
                ylabel='Leiden',
                prob=True)


if __name__ == '__main__':
    log = Pretty()
    root_path = Path('test-data/COMP-data/graph/nice')
    folders = [
        # all_years_f := root_path/Path('all_years/float'),
        # all_years_i := root_path/Path('all_years/int'),
        by_year_i := root_path/Path('by_year/int'),
        # by_year_f := root_path / Path('by_year/float'),
        # by_year_fs := root_path/Path('by_year/float_selfloop'),
    ]
    algorithms = ['leiden', 'louvain']
    nice_2018 = Path('test-data/COMP-data/graph/nice/by_year/int/nx_comp_nice_2018_int_graph')
    graph_nice_2018 = Path('test-data/COMP-data/graph/nice/by_year/int/nx_comp_nice_2018_int_graph.xml')

    # for algorithm in algorithms:
        # difference_matrix_by_year_members(algorithm, nice_2018)
        # difference_matrix_by_year_members_jaccard(algorithm, nice_2018)
        # difference_matrix_collaborations(algorithm, nice_2018, graph_nice_2018)

    for graph_folder in folders:
        for subfolder in graph_folder.iterdir():
            if os.path.isdir(subfolder):
                with log.scope.info(f'In {basename(subfolder)}'):
    #                 difference_matrix_leiden_louvain(subfolder)
                    difference_matrix_leidens(subfolder)

    # generate_data_for_algorithms()
