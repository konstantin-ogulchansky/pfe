"""
...
"""

import powerlaw as pl

from pfe.misc.log import timestamped
from pfe.misc.plot import Plot, red, blue
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

    # Compute the truncated degree distribution
    # (i.e., without points out of `(x_min, x_max)` range).
    truncated = original.truncate(x_min, x_max)
    truncated_normalized = truncated.normalized()

    # Plot the data.
    plot = Plot(tex=True)
    plot.scatter(truncated_normalized)

    # The empirical distribution.
    fit.plot_pdf(ax=plot.ax, color=red, linestyle='--', label='Empirical PDF')
    # The theoretical distribution.
    fit.power_law.plot_pdf(ax=plot.ax, color=blue, linestyle='-.', label='Power-Law PDF')

    plot.legend()
    plot.save('some-3.eps')
