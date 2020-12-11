"""
In order to test the hypothesis, 3 steps should be taken:

  1. Fit the data: this step is performed in order to find
     the optimal parameters of different distributions that fit
     the empirical data in the best way possible.

  2. Calculate the goodness-of-fit (Clauset et al.).

  3. Compare distributions via a likelihood ratio test: this step is
     needed to check which of the distributions is "the best" one
     since sometimes power law is selected by a mistake.
     For example, we could compare 'power-law' and 'lognormal' distributions
     (and, of course, other distributions).

  4. Test the hypothesis via K-S test.

TODO:
  - Check regular data?
  - Check binned data?
"""

import random
from decimal import Decimal
from math import floor
from typing import Iterable, Tuple, Any

import networkx as nx
import powerlaw as pl

from pfe.tasks.statistics import Statistic
from pfe.misc.log import Log, Nothing, Pretty, blue


def degree_distribution(graph: nx.Graph, weighted: bool = False) -> Statistic:
    """Computes the degree distribution distribution.

    :param graph: a `networkx.Graph`.
    :param weighted: whether the degree distribution should be weighted.

    :returns: a dictionary representing the distribution,
              where key is a degree and a value is the number
              of times this degree is found in the graph.
    """

    distribution = {}

    for node in graph.nodes:
        if weighted:
            degrees = graph.degree(weight='weight')
            degree = degrees[node]

            if isinstance(degree, Decimal):
                degree = int(degree.quantize(Decimal('1')))
            else:
                degree = round(degree)
        else:
            degree = graph.degree[node]

        distribution.setdefault(degree, 0)
        distribution[degree] += 1

    return Statistic(distribution)


def sample(cdf: dict[int, float], size: int, log: Log = Nothing()) -> Iterable[int]:
    """Draws a sample of the provided `size` according to `cdf`.

    This function implements the inverse transform sampling for drawing a sample
    according to an arbitrary distribution, defined by the provided CDF.

    Example:
    ::
        x = list(range(x_min, x_max + 1))
        y = fit.truncated_power_law.cdf(x)

        cdf = dict(zip(x, y))

        sampled = sample(cdf, size=1000)
        sampled = Statistic(Counter(sampled))

    .. [1] Wikipedia,
       https://en.wikipedia.org/wiki/Inverse_transform_sampling

    .. [2] "Inverse Transform Sampling",
       https://stephens999.github.io/fiveMinuteStats/inverse_transform_sampling.html
    """

    x = list(sorted(cdf.keys()))

    def draw(i: int) -> int:
        u = random.uniform(0, 1)
        p = 0

        log.info(f'Sampling {i}/{size} with `u` = {u}.')

        for i in range(len(x)):
            q = cdf[x[i]]

            if p <= u < q:
                return x[i]
            else:
                p = q

        log.error(f'The value for `u` = {u} was not found; returning {(m := max(x))}.')

        return m

    return (draw(i) for i in range(size))


def chi_squared(observed: dict[int, int], expected: dict[int, float]) -> float:
    """..."""

    x_min = min(expected.keys())
    x_max = max(expected.keys())

    assert all(x_min <= x <= x_max for x in observed.keys())

    n = sum(observed.values())

    def term(x):
        n_i = Decimal(observed[x]) / Decimal(n)
        p_i = Decimal(expected[x])

        return (n_i - p_i) ** 2 / p_i

    return n * sum(map(term, expected.keys()))


def bins(obs: dict[int, int], exp: dict[int, float], amount: int) \
        -> Tuple[dict[int, int], dict[int, float]]:
    """..."""

    x_min = min(exp)
    x_max = max(exp)
    width = floor((x_max - x_min + 1) / amount)

    new_obs = {}
    new_exp = {}

    x = x_min
    while x <= x_max:
        new_obs[x] = sum(obs.get(x + d, 0) for d in range(width))
        new_exp[x] = sum(exp.get(x + d, 0) for d in range(width))

        x += width

    return new_obs, new_exp


def normalized(dictionary: dict[Any, int]) -> dict[Any, int]:
    """..."""

    total = sum(dictionary.values())

    return {x: y / total for x, y in dictionary.items()}


if __name__ == '__main__':
    from pfe.parse import parse, publications_in

    log: Log = Pretty()
    log.info('Starting...')

    with log.info('Reading a graph...'):
        graph = parse(publications_in('COMP', between=(1990, 2018), log=log))

        log.info(f'Read a graph with '
                 f'{blue | graph.number_of_nodes()} nodes and '
                 f'{blue | graph.number_of_edges()} edges.')

    with log.info('Computing the degree distribution...'):
        original = degree_distribution(graph, weighted=True)

    with log.info('Fitting the hypothesis...'):
        fit = pl.Fit(list(original.sequence()), discrete=True)

    x_min = int(fit.xmin or original.min())
    x_max = int(fit.xmax or original.max())

    truncated = original.truncate(x_min, x_max)

    # x = list(sorted(truncated.keys()))
    x = list(range(x_min, x_max + 1))

    cdf = dict(zip(x, fit.truncated_power_law.cdf(x)))
    pdf = dict(zip(x, fit.truncated_power_law.pdf(x)))

    obs = {k: truncated[k] for k in sorted(truncated)}
    exp = pdf

    bin_obs, bin_exp = \
        bins(obs, exp, amount=21)

    statistic = chi_squared(bin_obs, bin_exp)

    print(f'Chi-squared statistic with {len(bin_exp)} bins:', statistic)

    print()
    for amount in range(2, 100):
        print(f'{amount:>3} bins:', chi_squared(*bins(obs, exp, amount)))
    print()
