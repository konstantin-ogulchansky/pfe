"""
TODO.
"""

import random
from typing import Iterable, Sequence

import powerlaw as pl

from pfe.misc.log.misc import percents
from pfe.misc.log import Log, Nothing


def sample(pdf: dict[int, float],
           size: int,
           resample: bool = False,
           log: Log = Nothing()) -> Iterable[int]:
    """Draws a sample of the provided ``size`` according to ``pdf``.

    This function implements the inverse transform sampling for drawing a sample
    according to an arbitrary distribution, defined by the provided PDF.

    Example. ::

        x = list(sorted(truncated.keys()))
        y = fit.truncated_power_law.pdf(x)

        pdf = dict(zip(x, y))

        sampled = sample(pdf, size=1000, resample=True)
        sampled = Statistic(sampled)

    .. [1] Wikipedia,
       https://en.wikipedia.org/wiki/Inverse_transform_sampling

    :param pdf: the probability density function
                according to which a sample should be drawn.
    :param size: the size of a sample to draw.
    :param resample: whether to resample an element in a case
                     if the generated probability is out of bounds of ``pdf``.
    :param log: an instance of ``Log`` to log steps of execution with.

    :return: the generated sample.
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
            log.warn(f'An element with `u` = {u} was not found; resampling.')
            return draw(i)

        raise ValueError(f'An element with `u` = {u} was not found.')

    return (draw(i) for i in range(1, size + 1))


def p_value(distribution: pl.Distribution, samples: Iterable[list[int]]) -> float:
    """Estimates p-value that can be used to test whether
    the provided distribution is a plausible fit to the data.

    .. [1] Aaron Clauset, Cosma Rohilla Shalizi, and M. E. J. Newman.
           "Power-law distributions in empirical data",
           SIAM Review, 51(4):661–703, November 2009.
           https://doi.org/10.1137/070710111
    """

    ks = distribution.KS()
    p = 0
    n = 0

    for sample in samples:
        p += distribution.KS(sample) > ks
        n += 1

    return p / n


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
