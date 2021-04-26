import csv
import json
from pathlib import Path

import numpy as np
import pandas as pd
import networkx as nx

from pfe.matrices.plot_heatmap import plot_matrix
from pfe.misc.log import Pretty, Log
from pfe.misc.style import blue, magenta

log: Log = Pretty()
log.info('Starting...')


def number_of_communities(louvain, data_path):
    if louvain:
        log.warn('Louvain')
        with log.scope.info('Reading communities ...'):
            with open(data_path / 'louvain_communities.json', 'r') as file:
                communities = json.load(file)
    else:
        log.warn('Leiden')
        with log.scope.info('Reading communities ...'):
            with open(data_path / 'leiden_communities.json', 'r') as file:
                communities = json.load(file)

    return len([x for x in communities.keys()])


def community_sizes(louvain, data_path):
    if louvain:
        with log.scope.info('Reading communities ...'):
            with open(data_path / 'louvain_communities.json', 'r') as file:
                communities = json.load(file)
    else:
        with log.scope.info('Reading communities ...'):
            with open(data_path / 'leiden_communities.json', 'r') as file:
                communities = json.load(file)

    community_size = {}

    for c in communities.keys():
        community_size[c] = len(communities[c])

    return community_size


def prob_matrix_by_row(k: pd.DataFrame):
    # k = k.copy()
    columns = k.columns.tolist()
    if 'sizes' in columns:
        columns.pop(columns.index('sizes'))

    for i in columns:
        n = sum([k.at[i, j] for j in columns])
        for j in columns:
            if k.at[i, j] == 0:
                continue
            k.at[i, j] /= n

    return k


def prob_matrix_by_all_publications(k: pd.DataFrame):
    k = k.copy()
    columns = k.columns.tolist()
    if 'sizes' in columns:
        columns.pop(columns.index('sizes'))

    s = 0
    for i in columns:
        for j in columns:
            if i >= j:
                s += k.at[i, j]

    print(s)
    for i in columns:
        for j in columns:
            k.at[i, j] /= s

    return k


def matrix(louvain, data_path, graph_path,  content='publication'):
    with log.scope.info(f'Preparing matrix content...{blue | content}'):

        if content in ['publication', 'publications', 'pub', 'p']:
            return publications_matrix(louvain=louvain, data_path=data_path)

        if content in ['collaboration', 'collaborations', 'collab', 'c']:
            return collaboration_matrix(louvain=louvain, data_path=data_path, graph_path=graph_path)


def publications_matrix(louvain, data_path):
    if louvain:
        log.warn("Louvain Method is used...")
    else:
        log.warn("Leiden Method is used...")

    n_communities = number_of_communities(louvain, data_path)
    matrix = np.zeros(shape=(n_communities, n_communities))

    with log.scope.info('Reading authors-communities...'):
        with open(data_path / 'stats_largest_cluster.json', 'r') as file:
            stats = json.load(file)

    with log.scope.info('Filling matrix...'):
        n = 0
        for s in stats:
            s.pop('publication_id')
            if len(s) == 2:
                n += 1
                c = []
                for i, k in zip(range(len(s)), s.keys()):
                    c.append(int(k.split()[1]))
                c.sort()
                matrix[c[0], c[1]] += 1
                matrix[c[1], c[0]] += 1

    log.info(f'# publications: {blue| n} \t# communities {blue| n_communities}')
    np.savetxt(data_path / f'mtr_{"louvain" if louvain else "leiden"}.csv', matrix, fmt='%d')

    return matrix


def collaboration_matrix(louvain, data_path, graph_path):
    if louvain:
        log.warn("Louvain Method is used...")
    else:
        log.warn("Leiden Method is used...")

    n_communities = number_of_communities(louvain=louvain, data_path=data_path)
    matrix = np.zeros(shape=(n_communities, n_communities))

    # networkx graph is more suitable for current tack
    with log.scope.info('Reading `nx.Graph`.'):
        graph = nx.read_weighted_edgelist(graph_path)

    log.info(f'Read a graph with '
             f'{blue | graph.number_of_nodes()} nodes and '
             f'{blue | graph.number_of_edges()} edges.')

    if louvain:
        with log.scope.info(f'Reading { blue| "Louvain" } communities ...'):
            with open(data_path / 'louvain_communities.json', 'r') as file:
                communities = json.load(file)
    else:
        with log.scope.info(f'Reading { blue| "Leiden" } communities ...'):
            with open(data_path / 'leiden_communities.json', 'r') as file:
                communities = json.load(file)

    log.warn(f'Number of {blue| "louvain" if louvain else "leiden"} communities: {blue | len(communities)}')

    with log.scope.info('Counting number of edges inside one community ...'):
        for c in communities.keys():
            # subset = [i for i in communities[c]]
            subset = [str(i) for i in communities[c]]
            if '0' in subset:
                subset.pop(subset.index('0'))

            subgraph = nx.subgraph(graph, subset).copy()
            matrix[int(c), int(c)] = subgraph.number_of_edges()

            # log.info(f'Subgraph of community #{c} '
            #          f'{blue | subgraph.number_of_nodes()} nodes and '
            #          f'{blue | subgraph.number_of_edges()} edges.')

    with log.scope.info('Counting number of edges between 2 communities ...'):
        communities_keys = list(communities.keys())

        for c in communities.keys():
            for cc in communities.keys():
                if c == cc:
                    continue

                n = 0
                for i in communities[c]:
                    for j in communities[cc]:
                        if i == 0 or j == 0:
                            continue
                        # n += graph.number_of_edges(int(i), int(j))
                        n += graph.number_of_edges(str(i), str(j))

                matrix[int(c), int(cc)] = n
                matrix[int(cc), int(c)] = n

            log.info(f'Community {blue | c} from {len(communities_keys)}')

    np.savetxt(data_path / f'mtr_collaborations_{"louvain" if louvain else "leiden"}.csv', matrix, fmt='%d')

    return matrix


def fill_diagonal(matrix: pd.DataFrame, data_path):
    ''' matrix diagonal will be filled with the number of publications inside community'''

    n_communities = matrix.columns.tolist()

    with log.scope.info('Reading authors-communities...'):
        with open(data_path / 'stats_largest_cluster.json', 'r') as file:
            stats = json.load(file)

    n = 0
    total = 0
    with log.scope.info('Filling matrix...'):
        for s in stats:
            s.pop('publication_id')
            total += 1
            if len(s) == 1:
                n += 1
                for k in s.keys():
                    c = k.split()[1]
                    if c in n_communities:
                        matrix[c][c] += 1

        # if prob:
        #     for i in n_communities:
        #         n = sum([matrix[i][j] for j in n_communities])
        #         for j in n_communities:
        #             if matrix[i][j] == 0:
        #                 continue
        #             matrix[i][j] /= n

    log.info(f'Number of considered publications: {blue | n}.\t Total {magenta | total}')
    # np.savetxt(test_stuff / 'mtr_wth_diagonal.csv', matrix, fmt='%.4f')

    return matrix


def add_row_with_community_size(m: pd.DataFrame, louvain, data_path):
    c_sizes = community_sizes(louvain, data_path)
    columns = m.columns.tolist()

    sizes = []
    for i in columns:
        sizes.append(c_sizes[i])

    m['sizes'] = sizes

    return m


def add_row_with_publication_number(m: pd.DataFrame, louvain, data_path):
    k = m.copy()

    n_communities = number_of_communities(louvain, data_path)
    df = pd. read_csv(data_path / 'mtr.csv', names=range(n_communities))

    publications = []
    for i in range(n_communities):
        n = sum([int(df[i][j]) for j in range(n_communities)])
        publications.append(n)

    # k['publications'] = publications
    print(publications)
    return k


def exclude_columns(m: pd.DataFrame, columns: list):
    k = m.drop(columns)
    k = k.transpose()
    k = k.drop(columns)
    k = k.transpose()

    print('exclude_columns ', columns)

    return k


def keep_columns(m: pd.DataFrame, columns: list):
    all = m.columns.tolist()

    print('keep_columns ', columns)

    if 'sizes' in all and 'sizes' not in columns:
        columns.append('sizes')

    odd = list(set(all).difference(columns))
    print('keep_columns odd ', odd)

    return exclude_columns(m, odd)


def to_dataframe(m, louvain, data_path):
    n_communities = number_of_communities(louvain, data_path)

    return pd.DataFrame(m, [str(i) for i in range(n_communities)], [str(i) for i in range(n_communities)])


def matrix_from_file(content:str, algorithm:str, data_path):
    if content in ['collaboration', 'collaborations', 'collab', 'c']:

        if algorithm.lower() == 'leiden':
            return np.loadtxt(data_path / 'mtr_collaborations_leiden.csv')

        elif algorithm.lower() == 'louvain':
            return np.loadtxt(data_path / 'mtr_collaborations_louvain.csv')

    elif content in ['publication', 'publications', 'pub', 'p']:

        if algorithm.lower() == 'leiden':
            return np.loadtxt(data_path / 'mtr_leiden.csv')

        elif algorithm.lower() == 'louvain':
            return np.loadtxt(data_path / 'mtr_louvain.csv')


if __name__ == '__main__':
    data_path = Path('test-data/COMP-data')
    # graph_path = Path('graph/nice')
    # m = matrix_from_file('p', 'louvain')
    matrix(louvain=False, content='c', data_path=data_path)
    # m = to_dataframe(m, louvain=False)
    # # fill_diagonal(m)
    # m = add_row_with_community_size(m, louvain=False)
    # m = prob_matrix_by_row(m)
    #
    # plot_matrix(m, 'all_communities (collaborations, leiden(CPM), prob by row)', exclude_columns=True, prob=True)

