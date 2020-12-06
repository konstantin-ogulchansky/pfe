"""
Test the hypothesis.
"""

import powerlaw as pl
import scipy.stats as st

from pfe.misc.log import timestamped, cx
from pfe.misc.plot import Plot
from pfe.parse import parse, publications_in
from pfe.tasks.hypothesis import degree_distribution, chi_squared


if __name__ == '__main__':
    log = timestamped
    log('Starting...')

    # Construct a graph.
    graph = parse(publications_in('COMP', between=(1990, 1996), log=log))

    log(f'Read a graph with '
        f'{graph.number_of_nodes()} nodes and '
        f'{graph.number_of_edges()} edges.')

    # Compute the statistic.
    with cx(log, 'Computing the statistic...'):
        statistic = degree_distribution(graph, weighted=True)

    # Fit the hypothesis.
    with cx(log, 'Computing the fit...'):
        fit = pl.Fit(list(statistic.sequence()), discrete=True)

    # Compute the "truncated" statistic (within [`x_min`, `x_max`]).
    x_min = fit.xmin or min(statistic.keys())
    x_max = fit.xmax or max(statistic.keys())

    if not isinstance(x_min, int):
        assert x_min.is_integer(), 'Strangely enough, `x_min` is not an integer.'
        x_min = round(x_min)

    if not isinstance(x_max, int):
        assert x_max.is_integer(), 'Strangely enough, `x_max` is not an integer.'
        x_max = round(x_max)

    truncated = statistic.truncate(x_min, x_max)

    x = list(sorted(truncated.keys()))

    cdf = dict(zip(x, fit.truncated_power_law.cdf(x)))
    pdf = dict(zip(x, fit.truncated_power_law.pdf(x)))

    assert abs(1 - sum(pdf.values())) <= 1e-3, '`sum p_i` must equal 1.'
    assert pdf.keys() == truncated.keys()

    # Plot PDF.
    plot = Plot(title='PDF')
    plot.scatter(truncated.normalized())
    plot.scatter(pdf, style={'color': 'red'})

    fit.truncated_power_law.plot_pdf(ax=plot.ax)

    plot.show()

    # Plot CDF.
    plot = Plot(title='CDF')
    plot.scatter(cdf, style={'color': 'red'})

    fit.truncated_power_law.plot_cdf(ax=plot.ax)

    plot.show()

    # Calculate the statistic.
    n = truncated.total()

    obs = [truncated[x] for x in sorted(truncated.keys())]
    exp = [pdf[x] * n for x in sorted(pdf.keys())]

    print(chi_squared(truncated.as_dict(), pdf))
    print(st.chisquare(obs, exp))
