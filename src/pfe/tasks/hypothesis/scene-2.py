"""
Test the hypothesis.
"""

import random
import sys
from collections import Counter, Callable
from typing import Iterable

import powerlaw as pl
import scipy.stats as st

from pfe.misc.log import timestamped, nothing, cx
from pfe.misc.plot import Plot
from pfe.parse import parse, publications_in
from pfe.tasks.hypothesis import degree_distribution
from pfe.tasks.statistics import Statistic


def sample(cdf: dict[int, float], size: int, log: Callable = nothing) -> Iterable[int]:
    """Draws a sample of the provided `size` according to `cdf`.

    This function implements the inverse transform sampling for drawing a sample
    according to an arbitrary distribution, defined by the provided CDF.

    .. [1] Wikipedia,
       https://en.wikipedia.org/wiki/Inverse_transform_sampling
    .. [2] Inverse Transform Sampling,
       https://stephens999.github.io/fiveMinuteStats/inverse_transform_sampling.html
    """

    x = list(sorted(cdf.keys()))

    def draw(i: int) -> int:
        u = random.uniform(0, 1)
        p = 0

        log(f'Sampling {i}/{size} with `u` = {u}.')

        for i in range(len(x)):
            q = cdf[x[i]]

            if p <= u < q:
                return x[i]
            else:
                p = q

        log(f'The value for `u` = {u} was not found; returning {(m := max(x))}.',
            file=sys.stderr)

        return m

    return (draw(i) for i in range(size))


if __name__ == '__main__':
    log = timestamped
    log('Starting...')

    # Construct a graph.
    graph = parse(publications_in('COMP', between=(1990, 2018), log=log))

    log(f'Read a graph with '
        f'{graph.number_of_nodes()} nodes and '
        f'{graph.number_of_edges()} edges.')

    # Compute the statistic.
    with cx(log, 'Computing the statistic...'):
        statistic = degree_distribution(graph, weighted=True)

    # Fit the hypothesis.
    with cx(log, 'Computing the fit...'):
        fit = pl.Fit(list(statistic.sequence()), discrete=True)

    # Compute the "truncated" statistic (within (`x_min`, `x_max`)).
    x_min = fit.xmin or min(statistic.keys())
    x_max = fit.xmax or max(statistic.keys())

    if not isinstance(x_min, int):
        assert x_min.is_integer(), 'Strangely enough, `x_min` is not an integer.'
        x_min = round(x_min)
    if not isinstance(x_max, int):
        assert x_max.is_integer(), 'Strangely enough, `x_max` is not an integer.'
        x_max = round(x_max)

    truncated = statistic.truncate(x_min, x_max)

    # Generate a sample.
    with cx(log, 'Generating a sample...'):
        x = list(range(x_min, x_max + 1))
        y = fit.truncated_power_law.cdf(x)
        cdf = dict(zip(x, y))

        sampled = sample(cdf, size=100000)
        sampled = Statistic(Counter(sampled)).cdf()

    # Plot.
    plot = Plot(log=log)

    plot.scatter(truncated.cdf())
    plot.scatter(cdf, style={'color': 'red'})
    plot.scatter(sampled, style={'color': 'green'})

    fit.truncated_power_law.plot_cdf(ax=plot.ax)

    plot.show()

    # Perform a K-S test.
    with cx(log, 'Performing K-S test...'):
        test = st.kstest(list(statistic.sequence()), sampled)
