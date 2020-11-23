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

from itertools import combinations

import networkx as nx
import powerlaw as pl

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
    from pfe.parse_cleaned_data import parse, publications_from
    from pfe.misc.log import timestamped

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

    comparison = {(a, b): fit.distribution_compare(a, b)
                  for a, b in combinations(distributions, r=2)}

    log('\n' + '\n'.join(f"    {a:<25} {b:<25}: {ratio}"
                         for (a, b), ratio in comparison.items()))

    alpha = fit.power_law.alpha
    sigma = fit.power_law.sigma
    x_min = fit.power_law.xmin
    x_max = fit.power_law.xmax

    log(f'Estimated power-law parameters: \n'
        f'    α: {alpha} \n'
        f'    σ: {sigma} \n'
        f'    x: {(x_min, x_max)}')
