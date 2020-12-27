"""
A model that generates hypergraphs whose degree distribution follows
a power-law distribution with an exponential cutoff.
"""

from dataclasses import dataclass, asdict
from typing import Callable

import numpy as np
import powerlaw as pl

from pfe.misc import distributions
from pfe.misc.log import Pretty, Log, Nothing, suppress_stderr
from pfe.misc.log.misc import percents
from pfe.misc.plot import Plot
from pfe.misc.style import magenta, blue
from pfe.tasks.distributions import Distribution


@dataclass
class Parameters:
    # noinspection PyUnresolvedReferences
    """Parameters of the model.

    :param n0: the initial number of nodes.
    :param n: the final number of nodes.
    :param p: the probability to add a node.
    :parma q: the probability to add an edge.
    :param d: the distribution of the cardinalities of hyperedges.
    """

    n0: int
    n: int
    p: float
    q: float
    d: Callable[[], int]

    def __post_init__(self):
        """Validates parameters of the model."""

        if not 0 < self.n0 <= self.n:
            raise ValueError('`n0` and `n` must be positive and `n0 <= n`.')

        if not 0 <= self.p <= 1:
            raise ValueError('`p` must be in the range [0, 1].')
        if not 0 <= self.q <= 1:
            raise ValueError('`q` must be in the range [0, 1].')


class Hypergraph:
    """A hypergraph generated according to the model.

    :param nodes: a list of nodes.
    :param edges: a list of hyperedges
                  (each hyperedge is represented as a list of vertices).
    """

    def __init__(self,
                 nodes: list[int],
                 edges: list[list[int]],
                 degree: list[int],
                 active: list[bool]):
        """Initialises the graph."""

        self.nodes = nodes
        self.edges = edges
        self.degree = degree
        self.active = active

    @classmethod
    def generate(cls, parameters: Parameters, log: Log = Nothing()) -> 'Hypergraph':
        """Generates a graph according to the model with the provided parameters."""

        graph = cls.initial(parameters)
        steps = 0

        while graph.number_of_nodes() < parameters.n:
            p = np.random.uniform()
            q = np.random.uniform()

            if p <= parameters.p:
                graph.add_node(parameters)
            else:
                if q <= parameters.q:
                    graph.add_edge(parameters)
                else:
                    graph.deactivate_node(parameters)

            if (steps := steps + 1) % 1000 == 0:
                log.info(f'Step {magenta | steps}.'.ljust(23) +
                         f'Nodes: {blue | graph.number_of_nodes()}, '.ljust(23) +
                         f'Edges: {blue | graph.number_of_edges()}. '.ljust(25) +
                         f'[{percents(graph.number_of_nodes(), parameters.n)}]')

        return graph

    @classmethod
    def initial(cls, parameters: Parameters) -> 'Hypergraph':
        """Generates the initial graph according to the model."""

        graph = Hypergraph(nodes=[],
                           edges=[],
                           degree=[0] * parameters.n,
                           active=[True] * parameters.n)

        for _ in range(parameters.n0):
            graph.add_node(parameters)

        return graph

    def number_of_nodes(self) -> int:
        """Returns the number of nodes in the graph."""
        return len(self.nodes)

    def number_of_edges(self) -> int:
        """Returns the number of edges in the graph."""
        return len(self.edges)

    def add_node(self, _: Parameters):
        """Adds a node to the graph."""

        self.nodes.append(node := self.number_of_nodes())

        active = [n for n in self.nodes if self.active[n]]

        if len(active) >= (size := parameters.d()):
            edge = np.random.choice(active, size=size - 1)
            edge = np.append(edge, node)
            edge = list(edge)

            self.edges.append(edge)

            for x in edge:
                self.degree[x] += 1

    def add_edge(self, parameters: Parameters):
        """Adds an edge to the graph."""

        p = [self.degree[n] * self.active[n] for n in self.nodes]
        p = np.asarray(p, dtype=np.float64)
        p = p / p.sum()

        size = parameters.d()
        edge = np.random.choice(self.nodes, p=p, size=size)  # Should `replace=False` be set?

        self.edges.append(edge)

        for node in edge:
            self.degree[node] += 1

    def deactivate_node(self, _: Parameters):
        """Deactivate a node."""

        p = [self.degree[n] * self.active[n] for n in self.nodes]
        p = np.asarray(p, dtype=np.float64)
        p = p / p.sum()

        node = np.random.choice(self.nodes, p=p)

        self.active[node] = False


if __name__ == '__main__':
    log = Pretty()
    log.info('Starting.')

    with log.scope.info('Generating a graph.'):
        parameters = Parameters(
            n0=10,
            n=10**5,
            p=0.3,
            q=0.9,
            d=distributions.uniform(3, 4, 5)
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
        distribution = Distribution(graph.degree)
        fit = pl.Fit(distribution.as_list(), discrete=True)

    with log.scope.info('Plotting the distribution.'):
        Plot.distribution(distribution, fit).show()
    with log.scope.info('Plotting PDFs.'):
        Plot.pdfs(distribution, fit).show()
    with log.scope.info('Plotting CDFs.'):
        Plot.cdfs(distribution, fit).show()
    with log.scope.info('Plotting CCDFs.'):
        Plot.ccdfs(distribution, fit).show()
