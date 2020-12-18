"""
A model that generates hypergraphs.
"""

from collections import Counter
from dataclasses import dataclass, asdict, field
from itertools import product
from typing import Callable, Union

import numpy as np

from pfe.misc.errors import ಠ_ಠ
from pfe.misc.log import Pretty, Log, Nothing, suppress_stderr
from pfe.misc.log.misc import percents
from pfe.misc.plot import Plot
from pfe.misc.style import magenta, blue
from pfe.tasks.statistics import Statistic


@dataclass
class Parameters:
    # noinspection PyUnresolvedReferences
    """Parameters of the model.

    :param n0: the initial number of nodes.
    :param n: the final number of nodes.
    :param c: the number of communities.
    :param pv: a probability to add a node alone.
    :param pve: a probability to add a node + an edge.
    :param p: a square matrix of collaborations.
    :param m: a vector of probabilities to belong to a community.
    :param gamma: a probability to choose a node `u` is `deg(u) + gamma`.
    :param distribution: a distribution of the cardinalities of hyperedges.
    """

    n0: int
    n: int
    c: int
    pv: float
    pve: float
    p: Union[np.ndarray, list[list[float]]]
    m: Union[np.ndarray, list[float]]
    gamma: float
    distribution: Callable[[], int]

    class Aux:
        """Auxiliary fields that are convenient
        but are not parameters of the model."""

        def __init__(self, parameter: 'Parameters'):
            self.p_flat = parameter.p.flatten()
            self.communities = np.asarray(list(range(parameter.c)))
            self.communities_pairs = \
                np.asarray(list(product(self.communities, self.communities)))

    aux: Aux = field(init=False)

    def __post_init__(self):
        """Validates parameters of the model."""

        self.p = np.asarray(self.p)
        self.m = np.asarray(self.m)

        if self.n0 < self.c:
            raise ValueError('`n0` must be greater or equal to `c`.')
        if self.n0 > self.n:
            raise ValueError('`n0` must be less or equal to `n`.')

        if not 0 <= self.pv <= 1:
            raise ValueError('`pv` must be in the range [0, 1].')
        if not 0 <= self.pve <= 1:
            raise ValueError('`pve` must be in the range [0, 1].')

        if self.pv + self.pve > 1:
            raise ValueError('`pv + pve` must be less than 1.')

        if self.p.ndim != 2 or self.p.shape[0] != self.p.shape[1]:
            raise ValueError('`p` has an incorrect form.')
        if self.m.ndim != 1 or self.p.shape[0] != self.m.shape[0]:
            raise ValueError('`m` has an incorrect form.')

        if self.c != self.p.shape[0]:
            raise ValueError('`p` must be of size `c` by `c`.')

        if self.p.sum() != 1:
            raise ValueError('`p` must be normalised.')
        if self.m.sum() != 1:
            raise ValueError('`m` must be normalised.')

        self.aux = Parameters.Aux(self)


class Hypergraph:
    """A hypergraph generated according to the model.

    :param nodes: a list of communities of nodes.
    :param edges: a list of hyperedges (each hyperedge is represented
                  as a list of vertices).

    :param e:
        > list of list, each list corresponds to one community, and
        > contains a list of nodes repeated as their degrees; useful to pick
        > randomly a node depending of its degree (size ``c``)
    :param d: a list of degrees of nodes (``d[i] := deg(i)``).
    :param v:
        > list of the labels of hyperedges associated to each nodes (``v[0]`` is
        > the list of the label of the hyperedges the node `0` belongs to;
        > the correspondence between the label and the hyperedges can be found
        > using ``edges``).
    :param q: a list of communities of nodes
              (``q[i]`` is the community of the node `i`).
    """

    def __init__(self,
                 nodes: list[list[int]],
                 edges: list[list[int]],
                 e: list[list[int]],
                 v: list[list[int]],
                 d: list[int],
                 q: list[int]):
        """Initialises the graph."""

        self.nodes = nodes
        self.edges = edges

        self.e = e
        self.v = v
        self.d = d
        self.q = q

    @classmethod
    def generate(cls, parameters: Parameters, log: Log = Nothing()) -> 'Hypergraph':
        """Generates a graph according to the model with the provided parameters."""

        graph = cls.initial(parameters)
        steps = 0

        while graph.number_of_nodes() < parameters.n:
            u = np.random.random()

            if u < parameters.pv:
                graph.add_node(parameters)
            elif u < parameters.pv + parameters.pve:
                graph.add_node_and_edge(parameters)
            else:
                graph.add_edge(parameters)

            if (steps := steps + 1) % 1000 == 0:
                log.info(f'Step {magenta | steps}.'.ljust(23) +
                         f'Nodes: {blue | graph.number_of_nodes()}, '.ljust(23) +
                         f'Edges: {blue | graph.number_of_edges()}. '.ljust(25) +
                         f'[{percents(graph.number_of_nodes(), parameters.n)}]')

        return graph

    @classmethod
    def initial(cls, parameters: Parameters) -> 'Hypergraph':
        """Generates the initial graph according to the model."""

        e = [[] for _ in range(parameters.c)]
        v = [[] for _ in range(parameters.n)]
        d = [0  for _ in range(parameters.n)]
        q = []

        nodes = [[] for _ in range(parameters.c)]
        edges = []

        for node in range(parameters.n0):
            # Assign nodes to communities in a cyclic manner,
            # e.g., nodes will be assigned to 3 communities as
            # 0 -> 0, 1 -> 1, 2 -> 2, 3 -> 0, 4 -> 1, etc.
            community = node % parameters.c

            nodes[community].append(node)
            q.append(community)

        return Hypergraph(nodes, edges, e=e, v=v, d=d, q=q)

    def number_of_nodes(self) -> int:
        """Returns the number of nodes in the graph."""
        return len(self.q)

    def number_of_edges(self) -> int:
        """Returns the number of edges in the graph."""
        return len(self.edges)

    def add_node(self, parameters: Parameters):
        """Adds a node to the graph."""

        community = np.random.choice(parameters.aux.communities, p=parameters.m)

        self.nodes[community].append(len(self.q))
        self.q.append(community)

    def add_node_and_edge(self, parameters: Parameters):
        """Adds a node and an edge to the graph. Or does it?"""
        raise ಠ_ಠ("This shouldn't have happened...")

    def add_edge(self, parameters: Parameters):
        """Adds an edge to the graph."""

        # Select a random pair from `communities_pairs`.
        pair_idx = np.random.choice(parameters.aux.communities_pairs.shape[0], p=parameters.aux.p_flat)
        pair = parameters.aux.communities_pairs[pair_idx]

        q1, q2 = pair
        h1, h2 = parameters.distribution(), parameters.distribution()

        def hyperedge(q: int, h: int) -> list[int]:
            e = []
            x = len(self.nodes[q])  # The number of nodes in the community `q`.
            y = len(self.e[q])      # The sum of degrees of nodes in the community `q`.
            p = parameters.gamma * x / (y + parameters.gamma * x)

            # Pick `h` random nodes for a hyperedge.
            for _ in range(h):
                # Either we pick a completely random node because of `gamma`,
                # or according to degrees of nodes.
                if np.random.uniform() < p:
                    u = np.random.choice(self.nodes[q])
                else:
                    d = int(len(self.e[q]) * np.random.uniform())
                    u = self.e[q][d]

                e.append(u)

            return e

        e1 = hyperedge(q1, h1)
        e2 = hyperedge(q2, h2)

        self.edges.append(e1 + e2)

        for u in e1:
            self.v[u].append(len(self.edges))
            self.d[u] += 1
            self.e[q1].append(u)

        for u in e2:
            self.v[u].append(len(self.edges))
            self.d[u] += 1
            self.e[q2].append(u)


def normal(loc: float, scale: float) -> Callable[[], int]:
    """Returns a function that generates integer random values according to
    the normal (Gaussian) distribution with parameters `loc` and `scale`."""

    def next() -> int:
        return round(np.random.normal(loc=loc, scale=scale))

    return next


if __name__ == '__main__':
    log = Pretty()
    log.info('Starting.')

    np.set_printoptions(linewidth=np.inf, suppress=True)

    with log.scope.info('Generating a graph.'):
        parameters = Parameters(
            n0=10,
            n=10**4,
            c=2,
            pv=0.3,
            pve=0.0,
            p=[[0.25, 0.25],
               [0.25, 0.25]],
            m=[0.5, 0.5],
            gamma=20,
            distribution=lambda: 1,
        )

        with log.scope.info('Parameters.'):
            def flat(x: str) -> str:
                return x.replace('\n', '')

            for key, value in asdict(parameters).items():
                log.info(f'{str(magenta | key):<21} = {flat(str(value))}')

        graph = Hypergraph.generate(parameters, log=log)

        log.info(f'Generated a graph with '
                 f'{blue | graph.number_of_nodes()} nodes and '
                 f'{blue | graph.number_of_edges()} edges.')

    with log.scope.info('Computing the degree distribution.'), suppress_stderr():
        distribution = Statistic(Counter(graph.d))

        import powerlaw as pl

        fit = pl.Fit(list(distribution.sequence()), discrete=True)

        truncated = distribution.truncate(fit.xmin, fit.xmax)

    with log.scope.info('Plotting the distribution.'):
        plot = Plot(title='Degree Distribution (hyper)')
        plot.scatter(distribution)

        plot.x.label('Degree $k$')
        plot.x.scale('log')
        plot.x.limit(10**-1, 10**3)

        plot.y.label('Number of Nodes with Degree $k$')
        plot.y.scale('log')

        plot.show()

    with log.scope.info('Plotting CCDFs.'):
        plot = Plot(title='CCDF (hyper)')
        plot.scatter(truncated.ccdf())

        plot.x.label('Degree $k$')
        plot.x.scale('log')
        plot.x.limit(10**-1, 10**3)

        plot.y.label('$1 - F(k)$')
        plot.y.scale('log')

        fit.plot_ccdf(ax=plot.ax, label='Empirical')
        fit.power_law.plot_ccdf(ax=plot.ax, label='Power-Law')
        fit.truncated_power_law.plot_ccdf(ax=plot.ax, label='Power-Law with Cut-Off')

        plot.legend()
        plot.show()

    with log.scope.info('Plotting the fit.'), suppress_stderr():
        plot = Plot(title='Fit (hyper)')
        plot.scatter(truncated.normalized())

        plot.x.label('Degree $k$')
        plot.x.scale('log')
        plot.x.limit(10**-1, 10**3)

        plot.y.label('Fraction of Nodes with Degree $k$')
        plot.y.scale('log')

        fit.plot_pdf(ax=plot.ax, label='Empirical')
        fit.power_law.plot_pdf(ax=plot.ax, label='Power-Law')
        fit.truncated_power_law.plot_pdf(ax=plot.ax, label='Power-Law with Cut-Off')

        plot.legend()
        plot.show()
