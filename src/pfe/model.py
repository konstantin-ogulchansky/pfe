"""
A model that generates hypergraphs.
"""

from dataclasses import dataclass, asdict
from itertools import product
from typing import Callable, Union, Iterable

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
    :param pv: a probability to add a node alone.
    :param pve: a probability to add a node + an edge.
    :param p: a (`d`-dimensional "square") matrix of collaborations.
    :param m: a vector of probabilities to belong to a community.
    :param gamma: a probability to choose a node `u` is `deg(u) + gamma`.
    :param distribution: a distribution of the cardinalities of hyperedges.
    """

    n0: int
    n: int
    pv: float
    pve: float
    p: Union[np.ndarray, list[list[float]]]
    m: Union[np.ndarray, list[float]]
    gamma: float
    distribution: Callable[[], int]

    def __post_init__(self):
        """Validates parameters of the model."""

        self.p = np.asarray(self.p)
        self.m = np.asarray(self.m)

        if self.n0 < len(self.p):
            raise ValueError('`n0` must be greater or equal to the size of `p`.')
        if self.n0 > self.n:
            raise ValueError('`n0` must be less or equal to `n`.')

        if not 0 <= self.pv <= 1:
            raise ValueError('`pv` must be in the range [0, 1].')
        if not 0 <= self.pve <= 1:
            raise ValueError('`pve` must be in the range [0, 1].')

        # TODO: Ask.
        # Is this a correct check to add?
        if self.pv + self.pve > 1:
            raise ValueError('`pv + pve` must be less than 1.')

        if len(set(self.p.shape)) != 1 or len(self.p.shape) != self.p.shape[0]:
            raise ValueError('`p` has an incorrect form.')
        if self.m.ndim != 1 or self.p.shape[0] != self.m.shape[0]:
            raise ValueError('`m` has an incorrect form.')

        if self.p.sum() != 1:
            raise ValueError('`p` must be normalised.')
        if self.m.sum() != 1:
            raise ValueError('`m` must be normalised.')


class Graph:
    """A (hyper)graph generated according to the model."""

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

        # TODO: Ask.
        # What are these?
        self.e = e
        self.v = v  # Why do we need it? It doesn't seem to be used when generating a graph.
        self.d = d  # Degrees? This one is not used either.
        self.q = q  # And this one...

    @classmethod
    def generate(cls, parameters: Parameters) -> 'Graph':
        """Generates a graph according to the model with the provided parameters."""

        graph = cls.initial(parameters)

        while graph.number_of_nodes() < parameters.n:
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

        e = [[] for _ in range(len(parameters.p))]
        v = [[] for _ in range(parameters.n)]
        d = [0  for _ in range(parameters.n)]
        q = []

        for node in range(parameters.n0):
            # Assign nodes to communities in a cyclic manner,
            # e.g., nodes will be assigned to 3 communities as
            # 0 -> 0, 1 -> 1, 2 -> 2, 3 -> 0, 4 -> 1, etc.
            community = node % len(parameters.p)

            nodes[community].append(node)
            q.append(community)

        return Graph(nodes, edges, e=e, v=v, d=d, q=q)

    def number_of_nodes(self) -> int:
        """Returns the number of nodes in the graph."""
        return len(self.q)

    def add_node(self, parameters: Parameters):
        """Adds a node to the graph."""

        communities = np.asarray(list(range(len(parameters.p))))
        community = np.random.choice(communities, p=parameters.m)

        self.nodes[community].append(len(self.q))
        self.q.append(community)

    def add_node_and_edge(self, parameters: Parameters):
        """Adds a node and an edge to the graph. Or does it?"""

        # TODO: Ask.
        # Should there be an implementation? :)
        # Because currently we cannot specify `pve` other than 0.
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

        def hyperedge(q: int, h: int) -> Iterable[int]:
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

        # TODO: Ask.
        # Is it okay that `e1` and `e2` may contain duplicate nodes?
        # For example,, we can obtain a hyperedge like [1, 2, 1, 3].
        # This incorrectly affects the lists `v`, `d` and `e`, since the
        # duplicate node will be updated twice in the following loops.
        # For example, the degree of a node 1 will be updated twice,
        # even though we add only a single hyperedge.
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

            # TODO: Ask.
            # Shouldn't it be with `loc = 1` to generate a regular graph?
            # In the model, we concatenate two hyperedges of sizes 2,
            # which results in adding a hyperedge of size 4.
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
