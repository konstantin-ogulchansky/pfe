import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import networkx as nx
import igraph as ig
import numpy as np
import cdlib as cd

from pfe.matrices.matrix import matrix, difference, to_dataframe, prob_matrix_by_row, prob_matrix_by_all_publications, \
    number_of_communities
from pfe.matrices.plot_heatmap import plot_matrix
from pfe.misc.log import Pretty
from pfe.misc.style import blue
from pfe.parse import publications_in
import matplotlib.pyplot as plt

def p_matrix_year(year, graph, diagonal:bool, log=Pretty()):
    data_path_18 = Path('test-data/COMP-data/graph/nice/by_year/int/nx_comp_nice_2018_int_graph')

    with log.scope.info('Reading communities ...'):
        with open(data_path_18 / 'leiden_author-community.json', 'r') as file:
            communities = json.load(file)

    with log.scope.info('Collecting statistics...'):

        publications = list(publications_in('COMP', between=(1990, year)))
        log.info(f'{blue | len(publications)} publications.')

        stats = []
        publication_counter = 0
        for publication in publications:

            publication_counter += 1

            authors = []
            for author in publication['authors']:
                authors.append(author['id'])

            statistics = {'publication_id': publication['id']}

            all = True
            for id in authors:
                if str(id) not in graph.nodes():
                    all = False

            if all:
                for author in authors:
                    if str(author) in communities.keys():
                        community = f'community {communities[str(author)]}'

                        if community in statistics.keys():
                            statistics[community] += 1
                        else:
                            statistics[community] = 1

            stats.append(statistics)

    n_communities = number_of_communities(louvain=False, data_path=data_path_18)

    matrix = np.zeros(shape=(n_communities, n_communities))

    with log.scope.info('Filling matrix...'):
        n = 0
        for s in stats:
            s.pop('publication_id')
            if len(s) == 1 and diagonal:
                n += 1
                c = []
                for i, k in zip(range(len(s)), s.keys()):
                    c.append(int(k.split()[1]))
                matrix[c[0], c[0]] += 1
            if len(s) == 2:
                n += 1
                c = []
                for i, k in zip(range(len(s)), s.keys()):
                    c.append(int(k.split()[1]))
                c.sort()
                matrix[c[0], c[1]] += 1
                matrix[c[1], c[0]] += 1

    log.info(f'# publications: {blue| n} \t# communities {blue| n_communities}')
    # np.savetxt(data_path / f'mtr_{"louvain" if louvain else "leiden"}.csv', matrix, fmt='%d')

    return matrix

root_path = Path('test-data/COMP-data/graph/nice/by_year/int')
subfolder = lambda year: Path(root_path / f'nx_comp_nice_{year}_int_graph')
graph_path = lambda year: Path(root_path / f'nx_comp_nice_{year}_int_graph.xml')

algorithms = ['leiden']
contents = ['publications', 'collaborations']
content = 'publications'
versions = [True, False]

# for algorithm in algorithms:
for diagonal in versions:

    labex = []
    with open("C:/Users/2shel/Desktop/Labex.json", 'r', encoding='UTF-8') as file:
        labex_publications = json.load(file)

    for lp in labex_publications:
        labex.append(list(lp['ids'].values()))

    labex_communities = []
    for lp in labex_publications:
        labex_communities += list(lp['ids'].values())
    labex_communities = list(set(labex_communities))
    labex_communities.sort()

    labex_groups = []
    for lb in labex:
        for i in lb:
            for j in lb:
                if i == j and not diagonal:
                    continue
                labex_groups.append((i, j))
    labex_groups = list(set(labex_groups))

    matr_18 = p_matrix_year(2018, graph=nx.read_graphml(graph_path(2018)), diagonal=diagonal)
    matr_18_df = to_dataframe(matr_18)

    plot_matrix(matr_18_df,
                file_name=f'n_publications_18_communities_2018{"_no_diagonal"*(not diagonal)}',
                data_path=root_path,
                title=f'Publications matrix 2018',
                format="0.0f",
                prob=True, some=labex_groups)

    matr_18_df_prob = prob_matrix_by_row(matr_18_df)
    matr_18 = matr_18_df_prob.to_numpy(dtype=np.ndarray)

    for year in range(2013, 2018):
        graph_year = nx.read_graphml(graph_path(year))

        matr_year = p_matrix_year(year, graph_year, diagonal)

        matr_year_df = to_dataframe(matr_year)
        plot_matrix(matr_year_df,
                    file_name=f'n_publications_{year-2000}_communities_2018{"_no_diagonal"*(not diagonal)}',
                    data_path=root_path,
                    title=f'Publications matrix {year}',
                    subtitle='Communities from 2018',
                    format="0.0f",
                    prob=True, some=labex_groups)

        matr_year_df_prob = prob_matrix_by_row(matr_year_df)
        matr_year = matr_year_df_prob.to_numpy(dtype=np.ndarray)

        diff_matr = difference(matr_18, matr_year)
        diff_matr = to_dataframe(diff_matr)

        plot_matrix(diff_matr,
                    file_name=f'difference_{content}_18_{year-2000}_div_{18}_by_row{"_no_diagonal"*(not diagonal)}',
                    data_path=root_path,
                    title=f'Difference 2018 and {year} ',
                    subtitle=f'{content.capitalize()} prob by row \n Pij({2018})-Pij({year})/Pij({2018})',
                    format="0.2f",
                    prob=True, some=labex_groups)

        plot_matrix(matr_18_df.subtract(matr_year_df),
                    file_name=f'difference_{content}_18_{year - 2000}{"_no_diagonal"*(not diagonal)}',
                    data_path=root_path,
                    title=f'Difference 2018 and {year} ',
                    format="0.0f",
                    subtitle=f'{content.capitalize()} prob by row \n Publications({2018})-Publications({year})',
                    prob=True, some=labex_groups)

        labex_values = []
        for i, j in labex_groups:
            if i == j and not diagonal:
                continue
            labex_values.append(diff_matr.loc[str(i), str(j)])

        other_values = []
        for i in range(diff_matr.shape[0]):
            for j in range(diff_matr.shape[0]):
                if i == j and not diagonal:
                    continue
                if (i, j) not in labex_groups:
                    other_values.append(diff_matr.loc[str(i), str(j)])

        my_dict = {'All': other_values, 'Labex': labex_values}

        plt.clf()
        fig, ax = plt.subplots()
        ax.boxplot(my_dict.values())
        ax.set_xticklabels(my_dict.keys())

        ax.set_title(f'Boxplot 2018/{year}')

        plt.savefig(root_path / f'boxplot_{year}{"_no_diagonal"*(not diagonal)}.png')
