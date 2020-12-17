"""
A model that generates graph following
a power-law distribution with an exponential cutoff.
"""

from dataclasses import dataclass

import networkx as nx
import numpy as np

from pfe.misc.log import Log, Pretty, Nothing, suppress_stderr
from pfe.misc.plot import Plot
from pfe.misc.style import blue
from pfe.tasks.hypothesis import degree_distribution


@dataclass
class Parameters:
    # noinspection PyUnresolvedReferences
    """Parameters of the model.

    :param m: the size of the initial graph.
    :param n: the size of the final graph.
    :param p: the probability to add a new ball to `urn_1`;
              1 - p is the probability to select an urn
              with existing balls.
    :param q: the probability to transfer the selected ball from
              the selected `urn_i` to `urn_{i+1}`;
              1 - q is the probability to deactivate the ball.
    """

    m: int
    n: int
    p: float
    q: float

    def __post_init__(self):
        if self.m <= 0:
            raise ValueError('`m` must be positive.')
        if self.n <= 0:
            raise ValueError('`n` must be positive.')
        if self.m > self.n:
            raise ValueError('`n` must be greater or equal to `m`.')

        if not 0 < self.p < 1:
            raise ValueError('`p` must be in range (0, 1).')
        if not 0 < self.q <= 1:
            raise ValueError('`q` must be in range (0, 1].')


def generate(parameters: Parameters, log: Log = Nothing()) -> nx.Graph:
    """Generates a graph whose degree distribution follows
    a power law with an exponential cutoff.

    .. [1] Trevor Fenner, Mark Levene and George Loizou,
           "A model for collaboration networks giving rise to
            a power-law distribution with an exponential cutoff",
           Social Networks, vol. 29, no. 1, pp. 70–80, 2007.
           https://doi.org/10.1016/j.socnet.2005.12.003
    """

    # At the beginning, we only have a single
    # `urn_1` containing the first node.
    active_urns: dict[int, set[int]] = {1: set()}
    inactive_urns: dict[int, set[int]] = {}

    # Maps active balls to their urns.
    active_balls: dict[int, int] = {}

    # Generate the initial graph.
    graph = nx.Graph()

    for n in range(parameters.m):
        graph.add_node(n)

        active_urns[1].add(n)
        active_balls[n] = 1

    while graph.number_of_nodes() < parameters.n:
        p = np.random.uniform()
        q = np.random.uniform()

        if p <= parameters.p:
            # Insert a new ball to `urn_1`.
            graph.add_node(n := graph.number_of_nodes())

            active_urns[1].add(n)
            active_balls[n] = 1

            # NOTE: In "World-Wide Web scaling exponent from Simon’s 1955 model",
            # they propose to add an edge between the new node and an arbitrarily
            # chosen one. This would ensure that `urn_i` contains only balls with
            # degree `i`, and not with degree `i-1`.
        else:
            # Select a random `urn_i`.
            w = np.asarray([k * len(active_urns[k]) for k in active_urns], dtype=np.float64)
            w /= w.sum()

            i = np.random.choice(list(active_urns.keys()), p=w)
            j = np.random.choice(list(active_urns[i]))

            if q <= parameters.q:
                k = np.random.choice([k for k in active_balls.keys() if k != j])
                l = active_balls[k]

                # Transfer `ball_j` from `urn_i` to `urn_{i+1}`.
                active_urns[i].remove(j)
                active_urns.setdefault(i+1, set())
                active_urns[i+1].add(j)
                active_balls[j] = i+1

                # Transfer `ball_k` from `urn_l` to `urn_{l+1}`.
                active_urns[l].remove(k)
                active_urns.setdefault(l+1, set())
                active_urns[l+1].add(k)
                active_balls[k] = l+1

                graph.add_edge(j, k)
            else:
                # Deactivate `ball_j`.
                active_urns[i].remove(j)
                active_balls.pop(j)

                inactive_urns.setdefault(i, set())
                inactive_urns[i].add(j)

    return graph


if __name__ == '__main__':
    log = Pretty()
    log.info('Starting.')

    with log.scope.info('Generating a graph.'):
        parameters = Parameters(
            m=5,
            n=10000,
            p=0.5,
            q=1.0,
        )

        graph = generate(parameters, log=log)

        log.info(f'Generated a graph with '
                 f'{blue | graph.number_of_nodes()} nodes and '
                 f'{blue | graph.number_of_edges()} edges.')

    with log.scope.info('Computing the degree distribution.'):
        distribution = degree_distribution(graph)

    with log.scope.info('Plotting the distribution.'), suppress_stderr():
        plot = Plot(title='Degree Distribution')
        plot.scatter(distribution)

        plot.x.scale('log')
        plot.x.label('Degree $k$')
        plot.x.limit(10**-1, 10**3)

        plot.y.scale('log')
        plot.y.label('Number of Nodes with Degree $k$')

        plot.show()
