"""
A module for calculating statistics on collaboration networks.
"""

from typing import Any, Iterable, Iterator, Tuple, Optional

import networkx as nx
import community as cm


class Statistic:
    """A discrete statistic.

    :param p: a dictionary representing a discrete distribution.
    """

    __slots__ = ('_p', )

    def __init__(self, p: dict[int, int]):
        self._p = p

    def __iter__(self) -> Iterator[int]:
        """Returns an iterator over keys of the distribution."""
        return iter(self._p)

    def __getitem__(self, item: int) -> int:
        """Returns a value of the corresponding key of the distribution."""
        return self._p.get(item, 0)

    def keys(self) -> Iterable[int]:
        """Returns keys of the distribution."""
        return self._p.keys()

    def values(self) -> Iterable[int]:
        """Returns values of the distribution."""
        return self._p.values()

    def items(self) -> Iterable[Tuple[int, int]]:
        """Returns values of the distribution."""
        return self._p.items()

    def get(self, item: int, default: int) -> int:
        """Returns either value by key or the default value."""
        return self._p.get(item, default)

    def pop(self, item: int) -> int:
        """Removes a value by the specified key."""
        return self._p.pop(item)

    def cdf(self, inclusive: bool = False) -> dict[int, float]:
        """Computes the cumulative distribution function."""

        normalized = self.normalized()

        return {k: sum(normalized.get(l, 0) for l in range(k + 1 if inclusive else k))
                for k in normalized.keys()}

    def ccdf(self, inclusive: bool = True) -> dict[int, float]:
        """Computes the complementary cumulative distribution function."""

        normalized = self.normalized()
        maximum = max(normalized.keys())

        return {k: sum(normalized.get(l, 0) for l in range(k if inclusive else k + 1, maximum + 1))
                for k in normalized.keys()}

    def truncate(self,
                 min: Optional[float] = None,
                 max: Optional[float] = None) -> 'Statistic':
        """Truncates the statistic."""

        def truncate(x: dict[int, Any]) -> dict[int, Any]:
            if min is None and max is None:
                return dict(x)  # A copy of the original dictionary.

            def in_range(x):
                if min is not None and x < min:
                    return False
                if max is not None and x > max:
                    return False
                return True

            return {x: y for x, y in x.items() if in_range(x)}

        return Statistic(truncate(self._p))

    def as_sequence(self) -> Iterable[int]:
        """Returns the distribution values as a sequence."""

        for k, n in self._p.items():
            while (n := n - 1) >= 0:
                yield k

    def as_list(self) -> list[int]:
        """Returns the distribution values as a list."""
        return list(self.as_sequence())

    def as_dict(self) -> dict[int, int]:
        """Returns the distribution values as a dictionary."""
        return dict(self._p)

    def normalized(self) -> dict[int, float]:
        """Returns a normalized distribution."""

        total = self.total()

        return {k: n / total for k, n in self._p.items()}

    def total(self) -> int:
        """Returns the total number of observations."""
        return sum(self._p.values())

    def min(self) -> int:
        """Returns the minimum `x`."""
        return min(self._p.keys())

    def max(self) -> int:
        """Returns the maximum `x`."""
        return max(self._p.keys())

    def mean(self) -> float:
        """Returns the mean value."""
        return sum(k * n for k, n in self._p.items()) / self.total()


def number_of_authors(publications: list[dict]) -> int:
    """Computes the number of different authors.
    Authors are differentiated by their ID.

    :param: a list of publications.

    :return: the number of authors.
    """

    authors = set()
    for publication in publications:
        authors.update(x['id'] for x in publication['authors'])

    return len(authors)


def number_of_publications(publications: list[dict]) -> int:
    """Computes the number of publications.
    (This function exists rather for consistency.)

    :param: a list of publications.

    :return: the number of publications.
    """
    return len(publications)


def number_of_collaborations(graph: nx.Graph, weighted: bool = False) -> int:
    """Computes the number of [weighted] collaborations.

    The number of unweighted collaborations is the number
    of edges in the collaboration graph (excluding self-loops).

    The number of weighted collaborations is the total number
    of collaborations between different authors (i.e., if authors
    X and Y collaborated twice, then 2 will be added to the result).

    :param graph: a collaboration graph.
    :param weighted: whether to compute the number of weighted collaborations.

    :return: the number of [weighted] collaborations.
    """

    if not weighted:
        # The number of edges excluding self-loops.
        return sum(u != v for u, v in graph.edges)
    else:
        # The total number of collaborations between different authors.
        return sum(edge['collaborations']
                   for u, v, edge in graph.edges(data=True)
                   if u != v)


def publications_per_author(publications: list[dict]) -> Statistic:
    """Computes the distribution of publications per author.

    :param publications: a list of publications (in a raw format).

    :returns: a dictionary representing the distribution.
    """

    authors = {}

    for publication in publications:
        publication_authors = {int(x['id']) for x in publication['authors']}

        for author in publication_authors:
            authors.setdefault(author, 0)
            authors[author] += 1

    distribution = {}

    for publications in authors.values():
        distribution.setdefault(publications, 0)
        distribution[publications] += 1

    return Statistic(distribution)


def authors_per_publication(publications: list[dict]) -> Statistic:
    """Computes the distribution of authors per publication.

    :param publications: a list of publications (in a raw format).

    :returns: a dictionary representing the distribution.
    """

    distribution = {}

    for publication in publications:
        number = len({author['id'] for author in publication['authors']})

        distribution.setdefault(number, 0)
        distribution[number] += 1

    return Statistic(distribution)


def communities_per_publication(graph: nx.Graph, publications: Any) -> Statistic:
    """Computes the distributions of the number of communities per publication.

    TODO.

    :param graph: ...
    :param publications: ...

    :returns: ...
    """

    communities = cm.best_partition(graph)
    distribution = {}

    for publication in publications:
        try:
            partition = {communities[int(x['id'])] for x in publication['authors']}
            partition_size = len(partition)

            distribution.setdefault(partition_size, 0)
            distribution[partition_size] += 1
        except KeyError:
            pass

    return Statistic(distribution)


def partition_of_authors(graph: nx.Graph, publications: Any, partition_size: int):
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
