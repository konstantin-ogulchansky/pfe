"""
Plot the complementary cumulative distribution function.
"""

from itertools import combinations

import powerlaw as pl

from pfe.misc.collections import truncate
from pfe.misc.log import timestamped
from pfe.misc.plot import Plot, red, blue, green
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
    original = degree_distribution(graph, weighted=True)

    # Fit the hypothesis.
    fit = pl.Fit(list(original.sequence()), discrete=True)

    # Compare distributions.
    log('Comparing distributions...')

    comparison = {
        (a, b): fit.distribution_compare(a, b, normalized_ratio=True)
        for a, b in combinations(fit.supported_distributions, r=2)
    }

    log('\n' + '\n'.join(f'{a:>25}   {b:>25}   {comparison[a, b]}'
                         for a, b in comparison))

    # Plot the original data.
    plot = Plot(tex=True, log=log)
    plot.scatter(original.ccdf())

    plot.x.label('Degree $k$')
    plot.x.scale('log')
    plot.x.limit(10 ** -1, 10 ** 4)

    plot.y.label('$CCDF(k)$')
    plot.y.scale('log')
    plot.y.limit(10 ** -6, 10 ** 0)

    # Empirical CCDF.
    fit.plot_ccdf(ax=plot.ax, original_data=True, color=red, linestyle='--', label='Empirical PDF')

    plot.show()

    # Plot the truncated data.
    x_min = fit.power_law.xmin
    x_max = fit.power_law.xmax

    truncated = original.truncate(x_min, x_max)

    plot = Plot(tex=True, log=log)
    plot.scatter(truncated.ccdf())

    plot.x.label('Degree $k$')
    plot.x.scale('log')
    plot.x.limit(10 ** -1, 10 ** 4)

    plot.y.label('$CCDF(k)$')
    plot.y.scale('log')
    plot.y.limit(10 ** -6, 10 ** 0)

    fit.plot_ccdf(ax=plot.ax, color=red, linestyle='-.', label='Empirical CCDF')
    fit.power_law.plot_ccdf(ax=plot.ax, color=blue, linestyle='-.', label='Power-Law CCDF')
    fit.truncated_power_law.plot_ccdf(ax=plot.ax, color=green, linestyle='-.', label='Truncated Power-Law CCDF')

    plot.show()
