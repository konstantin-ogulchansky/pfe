"""
Test the hypothesis.
"""

import powerlaw as pl
import scipy.stats as st

from pfe.misc.log import Log, Pretty, blue
from pfe.misc.plot import Plot
from pfe.parse import parse, publications_in
from pfe.tasks.hypothesis import degree_distribution, chi_squared


if __name__ == '__main__':
    log: Log = Pretty()
    log.info('Starting...')

    # Construct a graph.
    with log.info('Reading a graph...'):
        graph = parse(publications_in('COMP', between=(1990, 2018), log=log))

        log.info(f'Read a graph with '
                 f'{blue | graph.number_of_nodes()} nodes and '
                 f'{blue | graph.number_of_edges()} edges.')

    # Compute the degree distribution.
    with log.info('Computing the degree distribution...'):
        statistic = degree_distribution(graph, weighted=True)

    # Fit the hypothesis.
    with log.info('Fitting the hypothesis...'):
        fit = pl.Fit(list(statistic.sequence()), discrete=True)

    # Compute the "truncated" statistic (within [`x_min`, `x_max`]).
    x_min = int(fit.xmin or min(statistic.keys()))
    x_max = int(fit.xmax or max(statistic.keys()))

    truncated = statistic.truncate(x_min, x_max)

    x = list(sorted(truncated.keys()))

    cdf = dict(zip(x, fit.truncated_power_law.cdf(x)))
    pdf = dict(zip(x, fit.truncated_power_law.pdf(x)))

    assert abs(1 - sum(pdf.values())) <= 1e-3, '`sum p_i` must equal 1.'
    assert pdf.keys() == truncated.keys()

    # Plot PDF.
    with log.info('Plotting PDF...'):
        plot = Plot(title='PDF')
        plot.scatter(truncated.normalized())
        plot.scatter(pdf, color='red')

        fit.truncated_power_law.plot_pdf(ax=plot.ax)

        plot.show()

    # Plot CDF.
    with log.info('Plotting CDF...'):
        plot = Plot(title='CDF')
        plot.scatter(cdf, color='red')

        fit.truncated_power_law.plot_cdf(ax=plot.ax)

        plot.show()

    # Compute the chi-square statistic.
    with log.info('Computing the χ² statistic...'):
        n = truncated.total()
        obs = [truncated[x] for x in sorted(truncated.keys())]
        exp = [pdf[x] * n for x in sorted(pdf.keys())]

        log.info('χ² (custom): ' + str(blue | chi_squared(truncated.as_dict(), pdf)))
        log.info('χ² (scipy):  ' + str(blue | st.chisquare(obs, exp)))
