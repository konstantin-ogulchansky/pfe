"""
Testing whether a power-law distribution is a plausible fit to the data.
"""

import json
from itertools import chain
from pathlib import Path
from typing import Iterable

import powerlaw as pl

from pfe.misc.log import Pretty, suppress_stderr
from pfe.misc.log.misc import percents
from pfe.misc.style import blue
from pfe.parse import parse, publications_in
from pfe.tasks.hypothesis import sample, p_value
from pfe.tasks.distributions import Distribution, degree_distribution


def samples_from(directory: Path) -> Iterable[list[int]]:
    """Reads a collection of samples from the specified directory."""

    for path in directory.iterdir():
        with open(path, 'r') as file:
            sample = json.load(file)
            sample = chain.from_iterable([int(k)] * v for k, v in sample.items())

            yield list(sample)


if __name__ == '__main__':
    log = Pretty()
    log.info('Starting.')

    data = Path('../../../../data/graph/nx')
    samples = 1000

    with log.scope.info('Reading a graph.'):
        graph = parse(publications_in('COMP', between=(1990, 2018), log=log))

    with log.scope.info('Computing the degree distribution.'):
        distribution = degree_distribution(graph)

    with log.scope.info('Fitting a power law.'), suppress_stderr():
        fit = pl.Fit(distribution.as_list(), discrete=True)

    with log.scope.info(f'Generating {samples} samples.'):
        x_min = fit.xmin or distribution.min()
        x_max = fit.xmax or distribution.max()

        # We need to increase the tail to make the obtained
        # `pdf` sum up as close to 1 as possible.
        d = 1000
        e = 1e-8

        x = list(range(int(x_min), int(x_max) + d + 1))
        y = fit.power_law.pdf(x)

        pdf = dict(zip(x, y))

        assert abs(1 - sum(pdf.values())) < e, \
            f'Must be closer to 1 than {sum(pdf.values())}.'

        # TODO:
        #   We need to implement another method to draw samples
        #   (refer to Clauset et al., 2009: generating synthetic data sets).
        for i in range(1, samples + 1):
            sampled = sample(pdf, size=graph.number_of_nodes())
            sampled = Distribution(sampled)

            with open(f'samples/sample-{i}.json', 'w') as file:
                json.dump(sampled.as_dict(), file)

            log.info(f'Sampled {i:>5}. [{percents(i, samples)}]')

    with log.scope.info(f'Testing the plausibility of a power law.'):
        p = p_value(fit.power_law, samples_from(Path('samples')))

        log.info(f'Estimated p-value: {blue | p}')
