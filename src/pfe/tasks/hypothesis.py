# TODO:
#    - check regular data
#    - check binned data?

import networkx as nx
import powerlaw as pl

from pfe.misc.collections import truncate
from pfe.tasks.statistics import Statistic


def degree_distribution(graph: nx.Graph) -> Statistic:
    """Computes the degree distribution distribution.

    :param graph: a `networkx.Graph`.

    :returns: a dictionary representing the distribution,
              where key is a degree and a value is the number
              of times this degree is found in the graph.
    """

    distribution = {}

    for node in graph.nodes:
        degree = graph.degree[node]

        distribution.setdefault(degree, 0)
        distribution[degree] += 1

    return Statistic(distribution)


if __name__ == '__main__':
    import matplotlib.pyplot as plt

    from pfe.parse_cleaned_data import parse, publications_from
    from pfe.misc.log import timestamped

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

    log = timestamped
    log('Starting...')

    domain = 'COMP'
    years = (1990, 2018)
    files = [f'../../../data/clean/{domain}/{domain}-{year}.json'
             for year in range(years[0], years[1] + 1)]

    # Construct a graph.
    graph = parse(publications_from(files, skip_100=True, log=log))

    log(f'Read a graph with '
        f'{graph.number_of_nodes()} nodes and '
        f'{graph.number_of_edges()} edges.')

    # Compute the "original" (not truncated) degree distribution.
    original = degree_distribution(graph)
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
        crosses := dict(s=25, color='black', marker='x'),
        circles := dict(s=25, facecolors='none', edgecolors='black'),
    ]

    plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman']})
    plt.rc('text', usetex=True)

    fig, axs = plt.subplots()

    # # Fig 1: raw original data.
    # ax = axs[0]
    # ax.grid(linestyle='--')
    # ax.set_axisbelow(True)
    # ax.scatter(original.keys(), original.values(), **circles)
    #
    # ax.set_xscale('log')
    # ax.set_yscale('log')
    #
    # ax.set_xlim(10 ** -1, 10 ** 4)
    # ax.set_ylim(10 ** -1, 10 ** 5)

    # Fig 2: normalized original data.
    included = truncate(original_normalized, x_min, x_max)
    excluded = {x: y for x, y in original_normalized.items() if x not in included}

    ax = axs
    ax.grid(linestyle='--')
    ax.set_axisbelow(True)
    ax.scatter(excluded.keys(), excluded.values(), **crosses)
    ax.scatter(included.keys(), included.values(), **circles)

    ax.set_xlim(10 ** -1, 10 ** 4)
    ax.set_ylim(10 ** -6, 10 ** 0)

    # Add vertical lines for `x_min` and `x_max`.
    def vertical_line(x, label, ax):
        ax.axvline(x=x, linestyle='dashed', color='black', linewidth=0.75)
        ax.text(x + 10, 0.005, fr'$x_{{{label}}} = {x}$', rotation=90)

    if x_min is not None:
        vertical_line(x=x_min, label='min', ax=ax)
    if x_max is not None:
        vertical_line(x=x_max, label='max', ax=ax)

    # The empirical distribution.
    fit.plot_pdf(ax=ax, original_data=True, color=red, linestyle='--')

    # # Fig 3: truncated data.
    # ax = axs[2]
    # ax.grid(linestyle='--')
    # ax.set_axisbelow(True)
    # ax.scatter(truncated_normalized.keys(), truncated_normalized.values(), **circles)
    #
    # # The empirical distribution.
    # fit.plot_pdf(ax=ax, color=red, linestyle='--')
    # # The theoretical distribution.
    # fit.power_law.plot_pdf(ax=ax, color=blue, linestyle='-.')

    plt.savefig('some.eps')
    plt.show()

    log('Finished plotting the data.')
    log('Done.')
