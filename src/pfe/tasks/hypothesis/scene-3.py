"""
Fit a power-law distribution into the degree distribution.
"""

import powerlaw as pl

from pfe.misc.collections import truncate
from pfe.misc.log import timestamped
from pfe.misc.plot import Plot, red, blue, crosses, circles, green
from pfe.parse import parse, publications_in
from pfe.tasks.hypothesis import degree_distribution


if __name__ == '__main__':
    log = timestamped
    log('Starting...')

    # Construct a graph.
    graph = parse(publications_in('COMP', between=(1990, 2018), log=log))

    log(f'Read a graph with '
        f'{graph.number_of_nodes()} nodes and '
        f'{graph.number_of_edges()} edges.')

    # Compute the degree distribution.
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
    included = truncate(original_normalized, x_min, x_max)
    excluded = {x: y for x, y in original_normalized.items() if x not in included}

    plot = Plot(tex=True)

    plot.x.label('Degree $k$')
    plot.x.scale('log')
    plot.x.limit(10 ** -1, 10 ** 4)

    plot.y.label('$P(k)$')
    plot.y.scale('log')
    plot.y.limit(10 ** -6, 10 ** 0)

    plot.scatter(excluded, crosses, label='Excluded Points')
    plot.scatter(included, circles, label='Included Points')

    if x_min is not None:
        plot.x.line(x_min, label=f'$x_{{min}} = {x_min}$')
    if x_max is not None:
        plot.x.line(x_max, label=f'$x_{{max}} = {x_max}$')

    # The empirical distribution.
    fit.plot_pdf(ax=plot.ax, original_data=True, color=red, linestyle='--', label='Empirical PDF')

    plot.legend()
    plot.save('some-3-a.eps')

    # Compute the truncated degree distribution
    # (i.e., without points out of `(x_min, x_max)` range).
    truncated = original.truncate(x_min, x_max)
    truncated_normalized = truncated.normalized()

    # Plot the data.
    plot = Plot(tex=True)
    plot.scatter(truncated_normalized)

    plot.x.label('Degree $k$')
    plot.x.scale('log')

    plot.y.label('$P(k)$')
    plot.y.scale('log')

    # The empirical distribution.
    fit.plot_pdf(ax=plot.ax, color=red, linestyle='--', label='Empirical PDF')
    # The theoretical power-law distribution.
    fit.power_law.plot_pdf(ax=plot.ax, color=blue, linestyle='-.', label='Power-Law PDF')
    # The theoretical truncated power-law distribution.
    fit.truncated_power_law.plot_pdf(ax=plot.ax, color=green, linestyle=':', label='Trunc. Power-Law PDF')

    plot.legend()
    plot.save('some-3-b.eps')
