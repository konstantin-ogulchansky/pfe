"""
...
"""

import matplotlib.pyplot as plt
import powerlaw as pl

from pfe.misc.log import timestamped
from pfe.parse_cleaned_data import publications_from, parse
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

    # Compute the truncated degree distribution
    # (i.e., without points out of `(x_min, x_max)` range).
    truncated = original.truncate(x_min, x_max)
    truncated_normalized = truncated.normalized()

    # Plot the data.
    colors = [
        red  := '#ff3f3f',
        blue := '#3f3fff',
    ]

    styles = [
        crosses := dict(s=25, color='black', marker='x'),
        circles := dict(s=25, facecolors='none', edgecolors='black'),
    ]

    plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman']})
    plt.rc('text', usetex=True)

    fig, ax = plt.subplots()

    ax.grid(linestyle='--')
    ax.set_axisbelow(True)

    ax.scatter(truncated_normalized.keys(), truncated_normalized.values(), **circles)

    # The empirical distribution.
    fit.plot_pdf(ax=ax, color=red, linestyle='--')
    # The theoretical distribution.
    fit.power_law.plot_pdf(ax=ax, color=blue, linestyle='-.')

    plt.savefig('some-3.eps')
    plt.show()
