"""
Plot the complementary cumulative distribution function.
"""

import powerlaw as pl

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

    x_min = fit.power_law.xmin
    x_max = fit.power_law.xmax

    truncated = original.truncate(x_min, x_max)

    # Plot the CDF.
    plot = Plot(tex=True, log=log)
    plot.scatter(truncated.cdf())

    plot.x.label('Weighted Degree $k$')
    plot.x.scale('log')
    plot.x.limit(10 ** -1, 10 ** 4)

    plot.y.label('$F(k)$')
    plot.y.scale('log')

    fit.plot_cdf(ax=plot.ax, color=red, label='Empirical CDF')
    fit.power_law.plot_cdf(ax=plot.ax, color=blue, label='Power-Law CDF')
    fit.truncated_power_law.plot_cdf(ax=plot.ax, color=green, label='Truncated Power-Law CDF')

    plot.legend(location='lower right')
    plot.save('some-5-a.eps')

    # Plot the CCDF.
    plot = Plot(tex=True, log=log)
    plot.scatter(truncated.ccdf())

    plot.x.label('Weighted Degree $k$')
    plot.x.scale('log')
    plot.x.limit(10 ** -1, 10 ** 4)

    plot.y.label('$\\overline{F}(k)$')
    plot.y.scale('log')

    fit.plot_ccdf(ax=plot.ax, color=red, label='Empirical CCDF')
    fit.power_law.plot_ccdf(ax=plot.ax, color=blue, label='Power-Law CCDF')
    fit.truncated_power_law.plot_ccdf(ax=plot.ax, color=green, label='Truncated Power-Law CCDF')

    plot.legend(location='lower left')
    plot.save('some-5-b.eps')
