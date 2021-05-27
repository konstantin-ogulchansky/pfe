import json
import os
from os.path import basename, splitext
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import networkx as nx
import igraph as ig
import numpy as np
from matplotlib import cm
from matplotlib.colors import ListedColormap
from matplotlib.patches import Rectangle

from pfe.matrices.by_community_size import plot_cumulative_community_sizes
from pfe.matrices.generate_data import create_data, create_data_cdlib_relabeled_graph, create_data_igraph
from pfe.matrices.generate_data_louvain import create_data_louvain
# from pfe.matrices.matrix import matrix, to_dataframe, fill_diagonal, \
#     add_row_with_community_size, prob_matrix_by_row, prob_matrix_by_all_publications
from pfe.matrices.semiusefull_stuff import get_mapping
from pfe.misc.log import Log, Pretty
from pfe.misc.style import blue, magenta

log: Log = Pretty()


def plot_matrix(m: pd.DataFrame, file_name, data_path: Path, some=[], title='', subtitle='', xlabel='', ylabel='',
                format=".4f",
                prob=False,
                exclude_columns=False):
    # if len(m.columns.tolist()) <= 1:
    #     return

    if exclude_columns:
        return plot_matrix_exclude_columns_from_heatmap(m, file_name, data_path, title, subtitle, xlabel, ylabel, prob)

    with log.scope.info('Plotting...'):
        plt.clf()
        if len(m.columns.tolist()) > 120:
            log.warn('To many communities to plot')
            return
        elif len(m.columns.tolist()) > 100 and prob:
            fig, ax = plt.subplots(figsize=(82, 82))
        elif len(m.columns.tolist()) > 45:
            fig, ax = plt.subplots(figsize=(64, 64))
        elif len(m.columns.tolist()) > 25:
            fig, ax = plt.subplots(figsize=(32, 32))
        else:
            fig, ax = plt.subplots(figsize=(16, 16))


        newcmp = 'seismic'

        if prob:
            ax = sns.heatmap(m, ax=ax, annot=True, fmt=format, cmap=newcmp, linewidths=.5, center=0)
        else:
            ax = sns.heatmap(m, ax=ax, annot=True, fmt=format, cmap=newcmp, linewidths=.5, center=0)

        for i, j in some:
            ax.add_patch(Rectangle((i, j), 1, 1, fill=False, edgecolor='red', lw=3))
            ax.add_patch(Rectangle((j, i), 1, 1, fill=False, edgecolor='red', lw=3))


        plt.xlabel(xlabel)
        plt.ylabel(ylabel)

        fig.suptitle(title, fontsize=40)
        ax.set_title(subtitle, fontdict=dict(ha='center', va='center', fontsize=20))
        ax.set_aspect("equal")

        plt.savefig(data_path / f'{file_name}.png')
        # plt.show()


def plot_matrix_exclude_columns_from_heatmap(m: pd.DataFrame, file_name, data_path: Path, title='', subtitle='',
                                             xlabel='', ylabel='', prob=False):
    m = m.sort_values(by='sizes', ascending=False)
    cols = m.columns.tolist()
    all_cols = len(cols)
    sizes_col = -1

    rows = list(m.index.values.tolist())

    if 'sizes' in cols:
        sizes_col = cols.index('sizes')
        cols.pop(sizes_col)
        rows.append('sizes')

    m = m[rows]
    prob_cols = len(cols)

    with log.scope.info('Plotting...'):
        plt.clf()
        if len(m.columns.tolist()) > 120:
            log.warn('To many communities to plot')
            return
        elif len(m.columns.tolist()) > 100 and prob:
            fig, ax = plt.subplots(figsize=(100, 100))
        elif len(m.columns.tolist()) > 45:
            fig, ax = plt.subplots(figsize=(82, 82))
        elif len(m.columns.tolist()) > 25:
            fig, ax = plt.subplots(figsize=(64, 64))
        else:
            fig, ax = plt.subplots(figsize=(32, 32))

        if prob:
            mask = np.zeros((prob_cols, all_cols))
            mask[:, prob_cols] = True
            ax = sns.heatmap(m, mask=mask, ax=ax, annot=True, fmt=".4f", cmap="YlGn", linewidths=.5,
                             vmin=m.values[:, :prob_cols].ravel().min(),
                             vmax=m.values[:, :prob_cols].ravel().max(),
                             annot_kws={"size": 20})

            for (j, i), label in np.ndenumerate(m.values):
                if i == sizes_col:
                    ax.text(i + 0.5, j + 0.5, label, fontdict=dict(ha='center', va='center', fontsize=20))

        else:
            mask = np.zeros((prob_cols, all_cols))
            mask[:, prob_cols] = True
            ax = sns.heatmap(m, mask=mask, ax=ax, annot=True, fmt=".0f", cmap="YlGn", linewidths=.5,
                             vmin=m.values[:, :prob_cols].ravel().min(),
                             vmax=m.values[:, :prob_cols].ravel().max(),
                             annot_kws={"size": 20})

            for (j, i), label in np.ndenumerate(m.values):
                if i == sizes_col:
                    ax.text(i + 0.5, j + 0.5, label, fontdict=dict(ha='center', va='center', fontsize=20))

        fig.suptitle(title, fontsize=80)
        ax.set_title(subtitle, fontdict=dict(ha='center', va='center', fontsize=70))
        ax.set_aspect("equal")

        plt.xlabel(xlabel)
        plt.ylabel(ylabel)

        plt.savefig(data_path / f'{file_name}.png')
        # plt.show()

#
# def make_plots(new_subdirectory: Path, algorithm_name: str, common_filename: str, graph_file, louvain: bool):
#     subname = algorithm_name
#     with log.scope.info(f'Plotting matrices (publications)'
#                         f' {magenta | subname + common_filename}'):
#         m = matrix(False, new_subdirectory, graph_file, 'p')
#         m = to_dataframe(m, False, new_subdirectory)
#         m = fill_diagonal(m, new_subdirectory)
#         m = add_row_with_community_size(m, louvain=False, data_path=new_subdirectory)
#         plot_name = common_filename.replace("_relabeled_nodes", "").replace("_", " ")
#
#         plot_cumulative_community_sizes(0.8, new_subdirectory, louvain)
#         plot_cumulative_community_sizes(0.9, new_subdirectory, louvain)
#         plot_cumulative_community_sizes(0.95, new_subdirectory, louvain)
#
#         plot_matrix(m, f'{plot_name} (publications, {subname})',
#                     new_subdirectory, title=f'Publications, {subname.capitalize()}',
#                     exclude_columns=True, prob=False)
#
#         plot_matrix(prob_matrix_by_row(m), f'{plot_name} (publications,{subname}, prob by row)',
#                     new_subdirectory,  title=f'Publications, {subname.capitalize()}',
#                     subtitle='values divided by the sum of the row',
#                     exclude_columns=True, prob=True)
#
#         plot_matrix(prob_matrix_by_all_publications(m),
#                     f'{plot_name} (publications, {subname}, prob by all publications)',
#                     new_subdirectory, title=f'Publications, {subname.capitalize()}',
#                     subtitle='values divided by the number of all publications',
#                     exclude_columns=True, prob=True)
#
#     with log.scope.info(f'Plotting matrices (collaborations) '
#                         f'{magenta | subname + common_filename}'):
#         m = matrix(louvain, new_subdirectory, graph_file, 'c')
#         m = to_dataframe(m, False, new_subdirectory)
#         m = add_row_with_community_size(m, louvain=louvain, data_path=new_subdirectory)
#
#         plot_matrix(m, f'{plot_name} (collaborations, {subname}',
#                     new_subdirectory, title=f'Collaborations, {subname.capitalize()}',
#                     exclude_columns=True, prob=False)
#
#         plot_matrix(prob_matrix_by_row(m), f'{plot_name} (collaborations,{subname}, prob by row)',
#                     new_subdirectory, title=f'Collaborations, {subname.capitalize()}',
#                     subtitle='values divided by the sum of the row',
#                     exclude_columns=True, prob=True)
#

# def bulk_plots():
#     '''
#     For each graph in a folder
#     Create a directory for a graph
#     Create a directories for generated data for each algorithm
#     Generate data for each algorithm in its folder
#     Generate matrices with no more than 120 communities
#     Generate plots with distributon of community sizes
#     '''
#
#     root_path = Path('test-data/COMP-data/graph/nice')
#     graph_folders = [
#         # by_year_f := root_path/Path('by_year/float'),
#         all_years_f := root_path/Path('all_years/float'),
#         all_years_i := root_path/Path('all_years/int'),
#         # by_year_i := root_path/Path('by_year/int'),
#         # by_year_fs := root_path/Path('by_year/float_selfloop'),
#     ]
#
#     log = Pretty()
#
#     for graph_folder in graph_folders:
#         for graph_file in graph_folder.iterdir():
#
#             # Leiden in igraph
#             if graph_file.suffix == '.net':
#                 with log.scope.info(f'Reading `ig.Graph`...{magenta | basename(graph_file)}'):
#                     graph = ig.Graph.Read_Pajek(str(graph_file))
#
#                     before = f'Read a graph with ' \
#                              f'{blue | len(graph.vs)} vertices and ' \
#                              f'{blue | len(graph.es)} edges.'
#                     log.info(before)
#
#                     graph = graph.clusters().giant()
#
#                     after = f'Subgraph with ' \
#                             f'{blue | len(graph.vs)} vertices and ' \
#                             f'{blue | len(graph.es)} edges.'
#                     log.info(after)
#
#                     log.info(get_mapping(graph_file, graph_folder))
#
#                 with log.scope.info("Leiden igraph"):
#                     algorithm = 'leiden ig '
#                     common_filename = splitext(basename(graph_file))[0].replace("_relabeled_nodes", '')
#
#                     with log.scope.info(f'Creating a folder...'
#                                         f'{magenta | algorithm + common_filename}'):
#                         new_subdirectory = graph_folder / (algorithm + common_filename)
#                         new_subdirectory.mkdir()
#
#                     with open(new_subdirectory / f'{common_filename} size.json', 'w') as file:
#                         json.dump(before + '\n' + after, file)
#
#                     create_data(graph, get_mapping(graph_file, graph_folder), new_subdirectory)
#
#                     make_plots(new_subdirectory, algorithm, common_filename, graph_file, False)
#
#             # used both algorithms but for NetworkX
#             if graph_file.suffix == '.txt' and 'relabeled' in graph_file.name:
#                 with log.scope.info(f'Reading `nx.Graph`... {magenta | basename(graph_file)}'):
#                     graph = nx.read_weighted_edgelist(graph_file)
#
#                     before = f'Read a graph with ' \
#                              f'{blue | graph.number_of_nodes()} nodes and ' \
#                              f'{blue | graph.number_of_edges()} edges.'
#                     log.info(before)
#
#                     largest_component = max(nx.connected_components(graph), key=len)
#                     graph = nx.subgraph(graph, largest_component)
#
#                     after = f'Subgraph of largest connected component ' \
#                             f'{blue | graph.number_of_nodes()} nodes and ' \
#                             f'{blue | graph.number_of_edges()} edges.'
#                     log.info(after)
#
#                     log.info(get_mapping(graph_file, graph_folder))
#
#                 # Louvain NetworkX
#                 with log.scope.info("Louvain NetworkX"):
#                     algorithm = 'louvain nx '
#                     common_filename = splitext(basename(graph_file))[0].replace("_relabeled_nodes", "")
#
#                     new_subdirectory = os.getcwd() / graph_folder / (algorithm + common_filename)
#                     with log.scope.info(f'Creating a folder...'
#                                         f'{magenta | algorithm + common_filename}'):
#                         new_subdirectory.mkdir()
#
#                     with open(new_subdirectory / f'{common_filename} size.json', 'w') as file:
#                         json.dump(before + '\n' + after, file)
#
#                     create_data_louvain(graph, get_mapping(graph_file, graph_folder), new_subdirectory)
#
#                     make_plots(new_subdirectory, algorithm, common_filename, graph_file, True)
#
#                 # Leiden NetworkX
#                 with log.scope.info("Leiden CDLib"):
#                     algorithm = 'leiden cdlib '
#                     common_filename = splitext(basename(graph_file))[0].replace("_relabeled_nodes", '')
#
#                     with log.scope.info(f'Creating a folder...'
#                                         f'{magenta | algorithm + common_filename}'):
#                         new_subdirectory = graph_folder / (algorithm + common_filename)
#                         new_subdirectory.mkdir()
#
#                     with open(new_subdirectory / f'{common_filename} size.json', 'w') as file:
#                         json.dump(before + '\n' + after, file)
#
#                     create_data_cdlib_relabeled_graph(graph, get_mapping(graph_file, graph_folder), new_subdirectory)
#
#                     make_plots(new_subdirectory, algorithm, common_filename, graph_file, False)
