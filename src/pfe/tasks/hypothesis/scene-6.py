"""
Test the hypothesis.
"""

import powerlaw as pl
import scipy.stats as st

from pfe.misc.log import timestamped
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

    # Compute the distribution.
    statistic = degree_distribution(graph, weighted=True)

    log('Computed the statistic.')

    # Fit the hypothesis.
    fit = pl.Fit(list(statistic.sequence()), discrete=True)

    log('Computed the fit.')

    # Compare distributions.
    comparison = {
        (a, b): fit.distribution_compare(a, b, normalized_ratio=True)
        for a in fit.supported_distributions
        for b in fit.supported_distributions
    }

    log('\n' + '\n'.join(f'{a:>25}   {b:>25}   {comparison[a, b]}'
                         for a, b in comparison))

    # Generate a sample.
    log('Generating a sample.')

    sample = fit.power_law.generate_random(1)

    log('Generated a sample.', sample)

    # Perform a K-S test.
    test = st.kstest(list(statistic.sequence()), sample)

    log('Performed a K-S test.', test)
