"""
...
"""

from dataclasses import dataclass, asdict
from itertools import product
from typing import Callable, Union

import numpy as np

from pfe.misc.errors import ಠ_ಠ
from pfe.misc.log import Log, Pretty
from pfe.misc.style import magenta


@dataclass
class Parameters:
    # noinspection PyUnresolvedReferences
    """Parameters of the model.

    :param n0: the initial number of nodes.
    :param n: the final number of nodes.
    :param pv: probability to add a node alone.
    :param pve: probability to add a node + an edge.
    :param p: the matrix of collaboration.
    :param m: the vector of probability to belong to a community.
    :param gamma: the probability to choose a node `u` is `deg(u) + gamma`.
    :param distribution: the distribution to be used.
    """

    n0: int
    n: int
    pv: float
    pve: float
    p: Union[np.ndarray, list[list[float]]]
    m: Union[np.ndarray, list[float]]
    gamma: float
    distribution: Callable[[], float]

    def __post_init__(self):
        """Validate parameters of the model."""

        self.p = np.asarray(self.p)
        self.m = np.asarray(self.m)

        if not 0 <= self.pv <= 1:
            raise ValueError('`pv` must be in [0, 1].')
        if not 0 <= self.pve <= 1:
            raise ValueError('`pve` must be in [0, 1].')

        if len(set(self.p.shape)) != 1 or len(self.p.shape) != self.p.shape[0]:
            raise ValueError('`p` has an incorrect form.')
        if self.m.ndim != 1 or self.p.shape[0] != self.m.shape[0]:
            raise ValueError('`m` has an incorrect form.')

        if self.p.sum() != 1:
            raise ValueError('`p` must be normalised.')
        if self.m.sum() != 1:
            raise ValueError('`m` must be normalised.')

        if self.n0 < len(self.p):
            raise ValueError('`n0` must be greater or equal to the size of `p`.')


class Graph:
    """A (hyper)graph generated according to the model."""

    def __init__(self, nodes, edges, d, e, v, q):
        self.nodes = nodes
        self.edges = edges

        # What are these?
        self.d = d
        self.e = e
        self.v = v
        self.q = q

    @classmethod
    def generate(cls, parameters: Parameters) -> 'Graph':
        """Generates a graph according to the model with the provided parameters."""

        graph = cls.initial(parameters)

        while len(graph.q) < parameters.n:
            u = np.random.random()

            if u < parameters.pv:
                graph.add_node(parameters)
            elif u < parameters.pv + parameters.pve:
                graph.add_node_and_edge(parameters)
            else:
                graph.add_edge(parameters)

        return graph

    @classmethod
    def initial(cls, parameters: Parameters) -> 'Graph':
        """Generates the initial graph according to the model."""

        nodes = [[] for _ in range(len(parameters.p))]
        edges = []

        d = [0  for _ in range(parameters.n)]
        v = [[] for _ in range(parameters.n)]
        e = [[] for _ in range(len(parameters.p))]
        q = []

        for node in range(parameters.n0):
            community = node % len(parameters.p)

            nodes[community].append(node)
            q.append(community)

        return Graph(nodes, edges, d, e, v, q)

    def add_node(self, parameters: Parameters):
        """Adds a node to the graph."""

        communities = np.asarray(list(range(len(parameters.p))))
        community = np.random.choice(communities, p=parameters.m)

        self.nodes[community].append(len(self.q))
        self.q.append(community)

    def add_node_and_edge(self, parameters: Parameters):
        """Adds a node and an edge to the graph. Or does it?"""
        raise ಠ_ಠ("This shouldn't have happened...")

    def add_edge(self, parameters: Parameters):
        """Adds an edge to the graph."""

        communities = np.asarray(list(range(len(parameters.p))))
        communities_pairs = np.asarray(list(product(communities, communities)))

        # Select a random pair from `communities_pairs`.
        pair_idx = np.random.choice(communities_pairs.shape[0], p=parameters.p.flatten())
        pair = communities_pairs[pair_idx, :]

        q1, q2 = pair
        h1, h2 = parameters.distribution(), parameters.distribution()

        def hyperedge(q, h):
            x = len(self.nodes[q])  # The number of nodes in the community `q`.
            y = len(self.e[q])      # The number of... something?
            p = parameters.gamma * x / (y + parameters.gamma * x)

            for _ in range(h):
                # Either we pick a completely random node because of `gamma`,
                # or according to degrees of nodes.
                if np.random.uniform() < p:
                    u = np.random.choice(self.nodes[q])
                else:
                    d = int(len(self.e[q]) * np.random.uniform())
                    u = self.e[q][d]

                yield u

        e1 = list(hyperedge(q1, h1))
        e2 = list(hyperedge(q2, h2))

        self.edges.append(e1 + e2)

        for u in e1:
            self.v[u].append(len(self.edges))
            self.d[u] += 1
            self.e[q1].append(u)

        for u in e2:
            self.v[u].append(len(self.edges))
            self.d[u] += 1
            self.e[q2].append(u)


def normal(loc: float, scale: float) -> Callable[[], float]:
    """Returns a function that generates random values according to
    the normal (Gaussian) distribution with parameters `loc` and `scale`."""

    def next() -> float:
        return round(np.random.normal(loc=loc, scale=scale))

    return next


if __name__ == '__main__':
    log: Log = Pretty()
    log.info('Starting.')

    np.set_printoptions(linewidth=np.inf, suppress=True)

    with log.info('Generating a graph.'):
        parameters = Parameters(
            n0=10,
            n=10**3,
            pv=0.3,
            pve=0.0,
            p=[[0.25, 0.25], [0.25, 0.25]],
            m=[0.5, 0.5],
            gamma=20,
            distribution=normal(loc=2, scale=0),
        )

        with log.info('Parameters.'):
            def flat(x: str) -> str:
                return x.replace('\n', '')

            for key, value in asdict(parameters).items():
                log.info(f'{str(magenta | key):<21} = {flat(str(value))}')

        data = Graph.generate(parameters)

        with log.info('Generated.'):
            log.info(f'{magenta | "nodes"} = {data.nodes}')
            log.info(f'{magenta | "edges"} = {data.edges}')
            log.info(f'{magenta | "d"}     = {data.d}')
            log.info(f'{magenta | "e"}     = {data.e}')
            log.info(f'{magenta | "v"}     = {data.v}')
            log.info(f'{magenta | "q"}     = {data.q}')
