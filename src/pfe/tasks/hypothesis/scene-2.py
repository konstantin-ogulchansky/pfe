"""
...
"""

import matplotlib.pyplot as plt
import powerlaw as pl

from pfe.misc.collections import truncate
from pfe.misc.log import timestamped
from pfe.parse import publications_from, parse
from pfe.tasks.hypothesis import degree_distribution


if __name__ == '__main__':
    log = timestamped
    log('Starting...')

    domain = 'COMP'
    years = (1990, 2018)
    files = [f'../../../../data/clean/{domain}/{domain}-{year}.json'
             for year in range(years[0], years[1] + 1)]

    # Construct a graph.
    graph = parse(publications_from(files, skip_100=True, log=log))

    log(f'Read a graph with '
        f'{graph.number_of_nodes()} nodes and '
        f'{graph.number_of_edges()} edges.')

    # Compute the "original" (not truncated) degree distribution.
    original = degree_distribution(graph)
    original_normalized = original.normalized()

    # Fit the hypothesis.
    fit = pl.Fit(list(original.sequence()), discrete=True)

    alpha = fit.power_law.alpha
    sigma = fit.power_law.sigma
    x_min = fit.power_law.xmin
    x_max = fit.power_law.xmax

    log(f'Estimated power-law parameters: \n'
        f'    α: {alpha} \n'
        f'    σ: {sigma} \n'
        f'    x: {(x_min, x_max)}')

    # Plot the data.
    colors = [
        red  := '#ff3f3f',
        blue := '#3f3fff',
    ]

    styles = [
        crosses := dict(s=25, color='black', marker='x'),
        circles := dict(s=25, facecolors='none', edgecolors='black'),
    ]

    included = truncate(original_normalized, x_min, x_max)
    excluded = {x: y for x, y in original_normalized.items() if x not in included}

    plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman']})
    plt.rc('text', usetex=True)

    fig, ax = plt.subplots()

    ax.grid(linestyle='--')
    ax.set_axisbelow(True)

    ax.scatter(excluded.keys(), excluded.values(), **crosses)
    ax.scatter(included.keys(), included.values(), **circles)

    ax.set_xlim(10 ** -1, 10 ** 4)
    ax.set_ylim(10 ** -6, 10 ** 0)

    # Add vertical lines for `x_min` and `x_max`.
    def vertical_line(x, label, ax):
        ax.axvline(x=x, linestyle='dashed', color='black', linewidth=0.75)
        ax.text(x + 10, 0.005, fr'$x_{{{label}}} = {x}$', rotation=90)

    if x_min is not None:
        vertical_line(x=x_min, label='min', ax=ax)
    if x_max is not None:
        vertical_line(x=x_max, label='max', ax=ax)

    # The empirical distribution.
    fit.plot_pdf(ax=ax, original_data=True, color=red, linestyle='--')

    plt.savefig('some-2.eps')
    plt.show()
