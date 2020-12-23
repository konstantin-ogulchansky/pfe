"""
A module for calculating statistics on collaboration networks.
"""

from collections import Counter
from decimal import Decimal
from typing import Any, Iterable, Iterator, Tuple, Optional, Union

import networkx as nx
import community as cm


class Distribution:
    """An empirical discrete probability distribution.

    Provides multiple convenient functions to analyse the distribution,
    such as ``pdf``, ``cdf``, ``ccdf``, etc.

    :param p: either a sequence of observed values or a dictionary that maps
              an observed value to the number of times it was observed.
    """

    __slots__ = ('_p', )

    def __init__(self, p: Union[Iterable[int], dict[int, int]]):
        if isinstance(p, dict):
            self._p = dict(sorted(p.items()))
        else:
            self._p = Counter(p)

        if not self._p:
            raise ValueError('The provided distribution is empty.')

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
        return self._p.items()  # NOQA.

    def get(self, item: int, default: int = 0) -> int:
        """Returns either value by key or the default value."""
        return self._p.get(item, default)

    def pop(self, item: int) -> int:
        """Removes a value by the specified key."""
        return self._p.pop(item)

    def pdf(self) -> dict[int, float]:
        """Returns the probability distribution function (PDF)."""

        size = self.size()

        return {k: n / size for k, n in self._p.items()}

    def cdf(self) -> dict[int, float]:
        """Computes the cumulative distribution function (CDF).

        CDF is defined as ``F(x) = P(X < x)``.
        """

        pdf = self.pdf()

        return {k: sum(pdf.get(l, 0) for l in range(k))
                for k in pdf.keys()}

    def ccdf(self) -> dict[int, float]:
        """Computes the complementary cumulative distribution function (CCDF),
        which is also known as the survival function.

        CCDF is defined as ``F̄(x) = 1 - F(x) = P(X >= x)``, where ``F(x)`` is CDF.
        """

        pdf = self.pdf()
        max = self.max()

        return {k: sum(pdf.get(l, 0) for l in range(k, max + 1))
                for k in pdf.keys()}

    def truncate(self,
                 min: Optional[float] = None,
                 max: Optional[float] = None) -> 'Distribution':
        """Returns a new distribution with observed values
        within the interval ``[min, max]``.

        If some element (``min`` or ``max``) is not specified, then
        the interval is unbounded from the corresponding side.

        :param min: the minimum element of the interval (optional).
        :param max: the maximum element of the interval (optional).

        :return: a new instance of truncated ``Distribution``.
        """

        def truncate(x: dict[int, Any]) -> dict[int, Any]:
            if min is None and max is None:
                return x

            def in_range(x):
                if min is not None and x < min:
                    return False
                if max is not None and x > max:
                    return False
                return True

            return {x: y for x, y in x.items() if in_range(x)}

        return Distribution(truncate(self._p))

    def size(self) -> int:
        """Returns the total number of the observed values."""
        return sum(self._p.values())

    def min(self) -> int:
        """Returns the minimum observed value."""
        return min(self._p.keys())

    def max(self) -> int:
        """Returns the maximum observed value."""
        return max(self._p.keys())

    def mean(self) -> float:
        """Returns the mean of the distribution."""
        return sum(k * n for k, n in self._p.items()) / self.size()

    def as_sequence(self) -> Iterable[int]:
        """Returns the observed values of the distribution as a sequence."""

        for k, n in self._p.items():
            while (n := n - 1) >= 0:
                yield k

    def as_list(self) -> list[int]:
        """Returns the observed values of the distribution as a list."""
        return list(self.as_sequence())

    def as_dict(self) -> dict[int, int]:
        """Returns the observed values of the distribution as a dict."""
        return dict(self._p)


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


def publications_per_author(publications: list[dict]) -> Distribution:
    """Computes the distribution of publications per author.

    :param publications: a list of publications (in a raw format).

    :return: the computed ``Distribution``.
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

    return Distribution(distribution)


def authors_per_publication(publications: list[dict]) -> Distribution:
    """Computes the distribution of the number of authors per publication.

    :param publications: a list of publications.

    :return: the computed ``Distribution``.
    """

    distribution = {}

    for publication in publications:
        number = len({author['id'] for author in publication['authors']})

        distribution.setdefault(number, 0)
        distribution[number] += 1

    return Distribution(distribution)


def communities_per_publication(graph: nx.Graph, publications: Any) -> Distribution:
    """Computes the distributions of the number of communities per publication.

    The function uses the Louvain method [1] to detect communities in the graph.

    .. [1] Vincent D. Blondel, Jean-Loup Guillaume, Renaud Lambiotte, and Etienne Lefebvre.
           "Fast unfolding of communities in large networks",
           Journal  of  Statistical  Mechanics:  Theory  and  Experiment, October 2008.
           https://doi.org/10.1088/1742-5468/2008/10/P10008.

    :param graph: the collaboration graph.
    :param publications: the list of publications that
                         the graph was constructed from.

    :return: the computed ``Distribution``.
    """

    graph = graph.copy()
    for edge in graph.edges:
        graph.edges[edge]['weight'] = float(graph.edges[edge]['weight'])

    communities = cm.best_partition(graph)
    distribution = {}

    for publication in publications:
        partition = {communities[int(x['id'])] for x in publication['authors']}
        partition_size = len(partition)

        distribution.setdefault(partition_size, 0)
        distribution[partition_size] += 1

    return Distribution(distribution)


def degree_distribution(graph: nx.Graph, weighted: bool = False) -> Distribution:
    """Computes the degree distribution distribution.

    :param graph: a `networkx.Graph`.
    :param weighted: whether the degree distribution should be weighted.

    :return: a dictionary representing the distribution,
             where key is a degree and a value is the number
             of times this degree is found in the graph.
    """

    distribution = {}

    for node in graph.nodes:
        if weighted:
            degrees = graph.degree(weight='weight')
            degree = degrees[node]

            if isinstance(degree, Decimal):
                degree = int(degree.quantize(Decimal('1')))
            else:
                degree = round(degree)
        else:
            degree = graph.degree[node]

        distribution.setdefault(degree, 0)
        distribution[degree] += 1

    return Distribution(distribution)
