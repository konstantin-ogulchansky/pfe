# TODO:
#    - check regular data
#    - check binned data?

from typing import Tuple

import powerlaw as pl

from pfe.tasks import statistics
from pfe.misc.collections import truncate
from pfe.tasks.statistics import Statistic


def fit(statistic: Statistic) -> Tuple[float, float, float, float]:
    """..."""

    # TODO: Implement.

    fit = pl.Fit(list(statistic.sequence()), discrete=True)

    # TODO: Remove.
    fit.plot_pdf(original_data=True)
    fit.plot_pdf()
    fit.power_law.plot_pdf(fit.data_original, color='black')
    fit.power_law.plot_pdf(color='yellow')

    # Check which distribution fits the best.
    # Probably there is a better distribution than the power law.
    print(fit.distribution_compare('power_law', 'lognormal', normalized_ratio=True))

    return (
        fit.power_law.alpha,
        fit.power_law.sigma,
        fit.power_law.xmin,
        fit.power_law.xmax
    )


if __name__ == '__main__':
    from itertools import combinations

    import matplotlib.pyplot as plt
    import networkx as nx

    from pfe.parse import parse, with_no_more_than
    import pfe.misc.log

    # In order to test the hypothesis, 3 steps should be taken:
    #   1. Fit the data: this step is performed in order to find
    #      the optimal parameters of different distributions that fit
    #      the empirical data in the best way possible.
    #   2. Calculate the goodness-of-fit (Clauset et al.).
    #   3. Compare distributions via a likelihood ratio test: this step is
    #      needed to check which of the distributions is "the best" one
    #      since sometimes power law is selected by a mistake.
    #      For example, we could compare 'power-law' and 'lognormal' distributions
    #      (and, of course, other distributions).
    #   4. Test the hypothesis via K-S test.

    verbose = True

    if verbose:
        log = pfe.misc.log.timestamped
    else:
        log = pfe.misc.log.nothing

    log('Starting...')

    # TODO: Uncomment when drawing plots for the report.
    # plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman']})
    # plt.rc('text', usetex=True)

    # Read the graph and calculate the statistic.
    publications = [f'../../../data/json/COMP-{year}.json' for year in range(1990, 2008 + 1)]
    graph = parse(publications, with_no_more_than(50, 'authors'),
                  log=log)

    log(f'Read a graph with '
        f'{graph.number_of_nodes()} nodes and '
        f'{graph.number_of_edges()} edges.')

    # Compute the "original" (not truncated) degree distribution.
    original = statistics.publications_per_author(graph)
    original_normalized = original.normalized()

    # Fit the hypothesis.
    fit = pl.Fit(list(original.sequence()), discrete=True)

    # Compare distributions.
    distributions = fit.supported_distributions.keys()

    log('Comparing distributions...')

    # comparison = {(a, b): fit.distribution_compare(a, b)
    #               for a, b in combinations(distributions, r=2)}
    #
    # log('\n' + '\n'.join(f"    {a:<25} {b:<25}: {ratio}"
    #                      for (a, b), ratio in comparison.items()))

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
    log('Plotting the data...')

    colors = [
        red  := '#ff3f3f',
        blue := '#3f3fff',
    ]

    styles = [
        crosses := dict(s=25, color='black', marker='x', alpha=0.75),
        circles := dict(s=25, facecolors='none', edgecolors='black', alpha=0.75),
    ]

    fig, axs = plt.subplots(3)

    # Fig 1: raw original data.
    ax = axs[0]
    ax.grid(linestyle='--')
    ax.scatter(original.keys(), original.values(), **circles)

    ax.set_xscale('log')
    ax.set_yscale('log')

    # Fig 2: normalized original data.
    included = truncate(original_normalized, x_min, x_max)
    excluded = {x: y for x, y in original_normalized.items() if x not in included}

    ax = axs[1]
    ax.grid(linestyle='--')
    ax.scatter(excluded.keys(), excluded.values(), **crosses)
    ax.scatter(included.keys(), included.values(), **circles)

    # Add vertical lines for `x_min` and `x_max`.
    def vertical_line(x, label, ax):
        ax.axvline(x=x, linestyle='dashed', color='black', linewidth=0.75)
        ax.text(x - 1, 0.001, fr'$x_{{{label}}} = {x}$', rotation=90)

    if x_min is not None:
        vertical_line(x=x_min, label='min', ax=ax)
    if x_max is not None:
        vertical_line(x=x_max, label='max', ax=ax)

    # The empirical distribution.
    fit.plot_pdf(ax=ax, original_data=True, color=red, linestyle='--')

    # Fig 3: truncated data.
    ax = axs[2]
    ax.grid(linestyle='--')
    ax.scatter(truncated_normalized.keys(), truncated_normalized.values(), **circles)

    # The empirical distribution.
    fit.plot_pdf(ax=ax, color=red, linestyle='--')
    # The theoretical distribution.
    fit.power_law.plot_pdf(ax=ax, color=blue, linestyle='-.')

    plt.show()

    log('Finished plotting the data.')
    log('Done.')
