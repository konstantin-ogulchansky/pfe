from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from pfe.misc.log import Log, Pretty

log: Log = Pretty()
log.info('Starting...')

# data_path = Path('test-data/COMP-data')


def plot_matrix(m: pd.DataFrame, file_name, data_path: Path, title='', subtitle='', xlabel='', ylabel='', prob=False,
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

        if prob:
            ax = sns.heatmap(m, ax=ax, annot=True, fmt=".4f", cmap="YlGn", linewidths=.5)
        else:
            ax = sns.heatmap(m, ax=ax, annot=True, fmt=".0f", cmap="YlGn", linewidths=.5)

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
