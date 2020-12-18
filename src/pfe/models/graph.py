"""
A model that generates graph following
a power-law distribution with an exponential cutoff.
"""

from dataclasses import dataclass
from typing import Optional

import networkx as nx
import numpy as np
import powerlaw as pl

from pfe.misc.log import Log, Pretty, Nothing, suppress_stderr
from pfe.misc.log.misc import percents
from pfe.misc.plot import Plot
from pfe.misc.style import blue, magenta
from pfe.tasks.hypothesis import degree_distribution


@dataclass
class Parameters:
    # noinspection PyUnresolvedReferences
    """Parameters of the model.

    :param p: the probability to add a new ball to `active_urn[1]`;
              1 - p is the probability to select an urn
              with existing balls.
    :param q: the probability to transfer the selected ball from
              the selected `active_urn[i]` to `active_urn[i+1]`;
              1 - q is the probability to deactivate the ball.
    :param m: the size of the initial graph.
    :param n: the size of the final graph (optional).
    :param k: the number of steps of the process (optional).
    """

    p: float
    q: float
    m: int
    n: Optional[int] = None
    k: Optional[int] = None

    def __post_init__(self):
        if not 0 < self.p < 1:
            raise ValueError('`p` must be in range (0, 1).')
        if not 0 < self.q <= 1:
            raise ValueError('`q` must be in range (0, 1].')

        # Cite: Fenner et al., 2005.
        # > It is necessary that, on average, more balls
        # > are added to the system than become inactive.
        if not (self.p > (1 - self.p) * (1 - self.q)):
            raise ValueError('`p > (1 - p) * (1 - q)` must hold.')

        if self.m <= 0:
            raise ValueError('`m` must be positive.')
        if self.n is None and self.k is None:
            raise ValueError('`n` or `k` must be specified.')

        if self.n is not None:
            if self.n <= 0:
                raise ValueError('`n` must be positive.')
            if self.n < self.m:
                raise ValueError('`n` must be greater or equal to `m`.')

        if self.k is not None:
            if self.k <= 0:
                raise ValueError('`k` must be positive.')


def generate(parameters: Parameters, log: Log = Nothing()) -> nx.Graph:
    """Generates a graph whose degree distribution follows
    a power law with an exponential cutoff.

    .. [1] Trevor Fenner, Mark Levene and George Loizou,
           "A model for collaboration networks giving rise to
           a power-law distribution with an exponential cutoff",
           Social Networks, vol. 29, no. 1, pp. 70–80, 2007.
           https://doi.org/10.1016/j.socnet.2005.12.003
    """

    active_urns: dict[int, set[int]] = {1: set()}
    inactive_urns: dict[int, set[int]] = {}

    # Maps active balls to their urns.
    active_balls: dict[int, int] = {}

    # Generate the initial graph.
    graph = nx.Graph()
    steps = 0

    for n in range(parameters.m):
        graph.add_node(n)

        active_urns[1].add(n)
        active_balls[n] = 1

    while True:
        if parameters.n is not None and graph.number_of_nodes() >= parameters.n:
            break
        if parameters.k is not None and steps >= parameters.k:
            break

        p = np.random.uniform()
        q = np.random.uniform()

        if p <= parameters.p:
            # Insert a new ball `n` to `active_urn[1]`.
            graph.add_node(n := graph.number_of_nodes())

            active_urns[1].add(n)
            active_balls[n] = 1

            # NOTE: In "World-Wide Web scaling exponent from Simon’s 1955 model",
            # they propose to add an edge between the new node and an arbitrarily
            # chosen one. This would ensure that `active_urn[i]` contains only
            # balls with degree `i`, and not with degree `i-1`.
        else:
            # Select a random `active_urn[i]`.
            w = np.asarray([k * len(active_urns[k]) for k in active_urns], dtype=np.float64)
            w /= w.sum()

            i = np.random.choice(list(active_urns.keys()), p=w)
            j = np.random.choice(list(active_urns[i]))

            if q <= parameters.q:
                k = np.random.choice([k for k in active_balls.keys() if k != j])
                l = active_balls[k]

                # Transfer ball `j` from `active_urn[i]` to `active_urn[i+1]`.
                active_urns[i].remove(j)
                active_urns.setdefault(i+1, set())
                active_urns[i+1].add(j)
                active_balls[j] = i+1

                # Transfer ball `k` from `active_urn[l]` to `active_urn[l+1]`.
                active_urns[l].remove(k)
                active_urns.setdefault(l+1, set())
                active_urns[l+1].add(k)
                active_balls[k] = l+1

                graph.add_edge(j, k)
            else:
                # Deactivate ball `j`.
                active_urns[i].remove(j)
                active_balls.pop(j)

                inactive_urns.setdefault(i, set())
                inactive_urns[i].add(j)

        if (steps := steps + 1) % 1000 == 0:
            if parameters.n is not None:
                progress = f'[{percents(graph.number_of_nodes(), parameters.n)}]'
            if parameters.k is not None:
                progress = f'[{percents(steps, parameters.k)}]'

            log.info(f'Step {magenta | steps}.'.ljust(23) +
                     f'Nodes: {blue | graph.number_of_nodes()}, '.ljust(23) +
                     f'Edges: {blue | graph.number_of_edges()}. '.ljust(25) +
                     progress)  # NOQA.

    return graph


if __name__ == '__main__':
    log = Pretty()
    log.info('Starting.')

    with log.scope.info('Generating a graph.'):
        parameters = Parameters(
            m=5,
            n=10**4,
            p=0.3,
            q=0.8,
            # k=1037021,
        )

        graph = generate(parameters, log=log)

        log.info(f'Generated a graph with '
                 f'{blue | graph.number_of_nodes()} nodes and '
                 f'{blue | graph.number_of_edges()} edges.')

    with log.scope.info('Saving the generated graph.'):
        nx.write_edgelist(graph, 'graph.txt')

    with log.scope.info('Computing the degree distribution.'):
        distribution = degree_distribution(graph)

    with log.scope.info('Fitting a power law.'), suppress_stderr():
        fit = pl.Fit(list(distribution.sequence()), discrete=True)

        comparison = fit.loglikelihood_ratio('power_law', 'truncated_power_law')
        truncated = distribution.truncate(fit.xmin, fit.xmax)

        log.info(f'Log-likelihood (PL, PL w/ C): {blue | comparison}.')

    with log.scope.info('Plotting the distribution.'), suppress_stderr():
        plot = Plot(title='Degree Distribution (new)')
        plot.scatter(distribution)

        plot.x.scale('log')
        plot.x.label('Degree $k$')
        plot.x.limit(10**-1, 10**3)

        if fit.xmin is not None:
            plot.x.line(fit.xmin)

        plot.y.scale('log')
        plot.y.label('Number of Nodes with Degree $k$')

        plot.show()

    with log.scope.info('Plotting the fit.'), suppress_stderr():
        plot = Plot(title='Fit (new)')
        plot.scatter(truncated.normalized())

        plot.x.scale('log')
        plot.x.label('Degree $k$')
        plot.x.limit(10**-1, 10**3)

        plot.y.scale('log')
        plot.y.label('Fraction of Nodes with Degree $k$')

        fit.plot_pdf(ax=plot.ax, label='Empirical')
        fit.power_law.plot_pdf(ax=plot.ax, label='Power Law')
        fit.truncated_power_law.plot_pdf(ax=plot.ax, label='Power Law with Cutoff')

        plot.legend()
        plot.show()

    with log.scope.info('Plotting CCDFs.'):
        plot = Plot(title='CCDF (new)')
        plot.scatter(truncated.ccdf())

        plot.x.label('Degree $k$')
        plot.x.scale('log')
        plot.x.limit(10**-1, 10**3)

        plot.y.label('1 - F(k)')
        plot.y.scale('log')

        fit.plot_ccdf(ax=plot.ax, label='Empirical')
        fit.power_law.plot_ccdf(ax=plot.ax, label='Power-Law')
        fit.truncated_power_law.plot_ccdf(ax=plot.ax, label='Power-Law with Cut-Off')

        plot.legend()
        plot.show()
