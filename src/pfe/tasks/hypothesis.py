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

  4. Test the hypothesis via the K-S test or the Pearson's chi-square test.
     - Test regular data?
     - Test binned data?
"""

import random
from decimal import Decimal
from typing import Iterable, Sequence

import networkx as nx

from pfe.misc.log.format import percents
from pfe.tasks.statistics import Statistic
from pfe.misc.log import Log, Nothing


def degree_distribution(graph: nx.Graph, weighted: bool = False) -> Statistic:
    """Computes the degree distribution distribution.

    :param graph: a `networkx.Graph`.
    :param weighted: whether the degree distribution should be weighted.

    :return: a dictionary representing the distribution,
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


def sample(pdf: dict[int, float],
           size: int,
           resample: bool = False,
           log: Log = Nothing()) -> Iterable[int]:
    """Draws a sample of the provided ``size`` according to ``pdf``.

    This function implements the inverse transform sampling for drawing a sample
    according to an arbitrary distribution, defined by the provided PDF.

    Example:
    ::
        x = list(sorted(truncated.keys()))
        y = fit.truncated_power_law.pdf(x)

        pdf = dict(zip(x, y))

        sampled = sample(pdf, size=1000, resample=True)
        sampled = Statistic(Counter(sampled))

    .. [1] Wikipedia,
       https://en.wikipedia.org/wiki/Inverse_transform_sampling

    .. [2] "Inverse Transform Sampling",
       https://stephens999.github.io/fiveMinuteStats/inverse_transform_sampling.html
    """

    x = list(sorted(pdf.keys()))

    def draw(i: int) -> int:
        u = random.uniform(0, 1)
        p = 0

        log.info(f'Sampling {i}/{size} [{percents(i, size)}] with `u` = {u}.')

        for j in range(len(x)):
            q = p + pdf[x[j]]

            if p <= u < q:
                return x[j]
            else:
                p = q

        if resample:
            log.warn(f'The value for `u` = {u} was not found; '
                     f'resampling.')
            return draw(i)
        else:
            log.error(f'The value for `u` = {u} was not found; '
                      f'returning {(m := max(x))}.')
            return m

    return (draw(i) for i in range(1, size + 1))


def histogram(data: dict[int, float], bins: Sequence[float]) -> list[float]:
    """...

    An example.
    ::
        obs = ...  # Observed values.
        exp = ...  # Expected values.

        bins = np.linspace(min(obs), max(obs))
        bins = np.logspace(log(min(obs), 10), log(max(obs), 10))

        bin_obs = histogram(obs, bins)
        bin_exp = histogram(exp, bins)

        chi = st.chisquare(bin_obs, bin_exp, ddof=1)
    """

    binned = []

    for i in range(len(bins) - 1):
        x_min = bins[i]
        x_max = bins[i + 1]

        if i < len(bins) - 2:
            within = lambda x: x_min <= x < x_max
        else:
            within = lambda x: x_min <= x <= x_max

        binned.append(sum(data[x] for x in data if within(x)))

    return binned


def chi_squared(observed: dict[int, int], expected: dict[int, float]) -> float:
    """...

    Should rather refer to ``scipy.stats.chisquare``.

    .. [1] Wikipedia,
       https://www.wikiwand.com/en/Pearson%27s_chi-squared_test

    .. [2] "Chi-Square Goodness-of-Fit Test",
       https://www.itl.nist.gov/div898/handbook/eda/section3/eda35f.htm
    """

    x_min = min(expected.keys())
    x_max = max(expected.keys())

    assert all(x_min <= x <= x_max for x in observed.keys())

    n = sum(observed.values())

    def term(x):
        n_i = Decimal(observed[x]) / Decimal(n)
        p_i = Decimal(expected[x])

        return (n_i - p_i) ** 2 / p_i

    return n * sum(map(term, expected.keys()))
