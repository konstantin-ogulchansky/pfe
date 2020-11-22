"""
A module for calculating statistics on collaboration networks.
"""

from typing import Any, Iterable, Iterator, Tuple, Optional
from itertools import chain

import networkx as nx

from pfe.misc.collections import truncate


class Statistic:
    """A discrete statistic.

    :param p: a dictionary representing a discrete distribution.
    """

    __slots__ = ('_p', '_n')

    def __init__(self, p: dict[int, int]):
        self._p = p
        self._n = sum(p.values())

    def __iter__(self) -> Iterator[int]:
        """Returns an iterator over keys of the distribution."""
        return iter(self._p)

    def __getitem__(self, item: int) -> int:
        """Returns a value of the corresponding key of the distribution."""
        return self._p[item]

    def keys(self) -> Iterable[int]:
        """Returns keys of the distribution."""
        return self._p.keys()

    def values(self) -> Iterable[int]:
        """Returns values of the distribution."""
        return self._p.values()

    def items(self) -> Iterable[Tuple[int, int]]:
        """Returns values of the distribution."""
        return self._p.items()

    def truncate(self,
                 min: Optional[float] = None,
                 max: Optional[float] = None) -> 'Statistic':
        """Truncates the statistic."""
        return Statistic(truncate(self._p, min, max))

    def sequence(self) -> Iterable[int]:
        """Returns the distribution values as a sequence.

        For example,
        >>> x = Statistic({1: 1, 2: 2})
        >>> list(x.sequence())
        [1, 2, 2]
        """
        return chain.from_iterable(
            [k] * n for k, n in self._p.items()
        )

    def normalized(self) -> dict[int, float]:
        """Returns a normalized distribution.

        For example,
        >>> x = Statistic({1: 1, 2: 2})
        >>> x.normalized()
        {1: 0.3333333333333333, 2: 0.6666666666666666}
        """
        return {k: n / self._n for k, n in self._p.items()}


def publications_per_author(graph: nx.Graph) -> Statistic:
    """Computes the distribution of publications per author.

    In fact, this is the degree distribution of the graph since nodes
    represent authors and edges represent publications. Thus, to calculate
    this statistic, we need to consider how many publication each author has
    (i.e., their degree in the graph).

    The degree distribution is defined as

        P(k) = n_k / n,

    where `n_k` is the number of nodes with the degree `k`, and `n` is the
    total number of nodes in the graph.

    :param graph: a `networkx.Graph`.

    :returns: a dictionary representing the degree distribution, where
              keys are degrees and values are their corresponding fractions
              in the graph.
    """

    # TODO:
    #   Is this the degree distribution though?
    #   Maybe not, considering that the degree distribution is a *fraction*
    #   of publications, while we need to count the number of publications.

    # TODO:
    #   Update the docstring.

    distribution = {}

    for node in graph.nodes:
        degree = graph.degree[node]

        distribution.setdefault(degree, 0)
        distribution[degree] += 1

    return Statistic(distribution)


def authors_per_publication(graph: nx.Graph, publications: Any) -> Statistic:
    """Computes the distribution of authors per publication."""

    # How do we even compute this, having a plain graph?
    # We need raw data to be able to differentiate publications
    # since edges of a graph do not contain this information.

    distribution = {}

    for publication in publications:
        number = len(publication.authors)

        distribution.setdefault(number, 0)
        distribution[number] += 1

    return Statistic(distribution)


def communities_per_publication(graph: nx.Graph, publications: Any) -> Statistic:
    """Computes the distributions of the number of communities per publication."""

    def louvain(_):
        raise NotImplementedError

    communities = louvain(graph)
    distribution = {}

    for publication in publications:
        partition = set()

        for author in publication.authors:
            community = next(x for x in communities if author.id in x)
            partition.add(community.id)

        distribution[len(partition)] += 1

    return Statistic(distribution)


def coauthors_partition(graph: nx.Graph, publications: Any, partition_size: int):
    """..."""

    def louvain(_):
        raise NotImplementedError

    communities = louvain(graph)
    proportions = []

    for publication in publications:
        partition = {}

        for author in publication.authors:
            community = next(x for x in communities if author.id in x)

            partition.setdefault(community.id, [])
            partition[community.id].append(author.id)

        if len(partition) != partition_size:
            continue

        # Append the proportion of authors from each community:
        # for authors in each community, yield the number of those authors
        # divided by the total number of authors of the publication.
        proportions.append(tuple(sorted(
            len(x) / len(publication.authors)
            for x in partition.values()
        )))

    return proportions


if __name__ == '__main__':
    import matplotlib.pyplot as plt

    from pfe.parse import parse, with_no_more_than
    from pfe.misc import log

    # plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman']})
    # plt.rc('text', usetex=True)

    # Construct a graph.
    publications = [f'../../../data/json/COMP-{year}.json' for year in range(1990, 2018 + 1)]
    graph = parse(publications, with_no_more_than(50, 'authors'),
                  log=log.timestamped)

    print()
    print('Nodes:', graph.number_of_nodes())
    print('Edges:', graph.number_of_edges())
    print()

    # Calculate statistics.
    statistic = publications_per_author(graph)
    normalized = statistic.normalized()

    # Plot statistics.
    styles = [
        crosses := dict(s=25, color='black', marker='x'),
        circles := dict(s=25, facecolors='none', edgecolors='black'),
    ]

    x = statistic.keys()
    y = statistic.values()

    plt.figure()

    ax = plt.gca()
    ax.set_axisbelow(True)
    ax.grid(linestyle='--')
    ax.scatter(x, y, **circles)

    ax.set_xscale('log')
    ax.set_yscale('log')

    ax.set_xlim(10 ** -1, 10 ** 4)
    ax.set_ylim(10 ** -1, 10 ** 5)

    # plt.savefig('first.eps', format='eps')

    plt.show()
