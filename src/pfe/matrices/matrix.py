import csv
import json
from pathlib import Path

import numpy as np
import pandas as pd

from pfe.matrices.plot_heatmap import plot_matrix
from pfe.misc.log import Pretty, Log

log: Log = Pretty()
log.info('Starting...')

test_stuff = Path('test-data/COMP-data')


def number_of_communities():
    with log.scope.info('Reading communities ...'):
        with open(test_stuff / 'leiden_communities.json', 'r') as file:
            communities = json.load(file)

    return len(communities.keys())


def community_sizes():
    with log.scope.info('Reading communities ...'):
        with open(test_stuff / 'leiden_communities.json', 'r') as file:
            communities = json.load(file)

    community_size = {}

    for c in communities.keys():
        community_size[c] = len(communities[c])

    return community_size


def prob_matrix_by_row(k: pd.DataFrame):
    k = k.copy()
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


def matrix():
    n_communities = number_of_communities()
    matrix = np.zeros(shape=(n_communities, n_communities))

    with log.scope.info('Reading authors-communities...'):
        with open(test_stuff / 'stats_largest_cluster.json', 'r') as file:
            stats = json.load(file)

    n = 0
    with log.scope.info('Filling matrix...'):
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
        #
        # if prob:
        #     for i in range(n_communities):
        #         n = sum([matrix[i][j] for j in range(n_communities)])
        #         for j in range(n_communities):
        #             if matrix[i][j] == 0:
        #                 continue
        #             matrix[i][j] /= n

    print(f'N: {n}')
    np.savetxt(test_stuff / 'mtr.csv', matrix, fmt='%d')

    return matrix


def fill_diagonal(matrix: pd.DataFrame):
    ''' matrix diagonal will be filled with the number of publications inside community'''

    n_communities = matrix.columns.tolist()

    with log.scope.info('Reading authors-communities...'):
        with open(test_stuff / 'stats_largest_cluster.json', 'r') as file:
            stats = json.load(file)

    n = 0
    with log.scope.info('Filling matrix...'):
        for s in stats:
            s.pop('publication_id')
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

    print(f'N: {n}')
    # np.savetxt(test_stuff / 'mtr_wth_diagonal.csv', matrix, fmt='%.4f')

    return matrix


def add_row_with_community_size(m: pd.DataFrame):
    c_sizes = community_sizes()
    columns = m.columns.tolist()

    sizes = []
    for i in columns:
        sizes.append(c_sizes[i])

    m['sizes'] = sizes

    return m


def add_row_with_publicaation_number(m: pd.DataFrame):
    k = m.copy()

    n_communities = number_of_communities()
    df = pd. read_csv(test_stuff/'mtr.csv', names=range(n_communities))

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


def to_dataframe(m):
    n_communities = number_of_communities()

    return pd.DataFrame(m, [str(i) for i in range(n_communities)], [str(i) for i in range(n_communities)])


if __name__ == '__main__':

    m = to_dataframe(matrix())
    fill_diagonal(m)

    plot_matrix(m, 'all_communities')
