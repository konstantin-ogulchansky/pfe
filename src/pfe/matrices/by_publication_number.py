from pathlib import Path
from pfe.misc.log import Pretty, Log
from pfe.matrices.matrix import matrix, fill_diagonal, prob_matrix, number_of_communities
from pfe.matrices.plot_heatmap import plot_matrix

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


log: Log = Pretty()
log.info('Starting...')

data = Path('../../../data/graph/ig')
test_stuff = Path('test-data')


def plot_cumulative_publications(matrix: pd.DataFrame):
    y = list(sorted(matrix.sum()))
    print(y)
    z = [sum(y[:i + 1]) for i in range(len(y))]

    plt.clf()
    plt.plot([x / len(y) for x in z])
    plt.ylabel('number of publications')
    # plt.axvline(x=percent)
    # plt.savefig(test_stuff / f'cut_{percent}p_of_communities_leaves_Np_of_publications.png')
    plt.savefig(test_stuff / f'cumulative_publications.png')
    plt.show()

    # plt.hist(y)
    sns.ecdfplot(y)
    plt.xlabel('number of publications')
    plt.savefig(test_stuff / f'cumulative_publications_cdf.png')
    plt.show()

    # return y[percent - 1]


def plot_matrix_restricted_by_publication_number(n_publications_in_community, diagonal=False):
    n_communities = number_of_communities()

    m = matrix()
    m = pd.DataFrame(m, [str(i) for i in range(n_communities)], [str(i) for i in range(n_communities)])

    if diagonal:
        m = fill_diagonal(m)

    odd_communities = []
    for i, p in zip(range(n_communities), m.sum()):
        if p < n_publications_in_community:
            odd_communities.append(str(i))

    odd_communities_2 = []
    for i, p in zip(range(n_communities), m.transpose().sum()):
        if p < n_publications_in_community:
            odd_communities_2.append(str(i))

    odd_communities = list(set(odd_communities).intersection(odd_communities_2))
    odd_communities.sort()

    k = m.drop(odd_communities)
    k = k.transpose()
    k = k.drop(odd_communities)
    k = k.transpose()

    k = prob_matrix(k)

    plot_matrix(k, f'matrix_restricted_by_publication_number_{n_publications_in_community}', prob=True)