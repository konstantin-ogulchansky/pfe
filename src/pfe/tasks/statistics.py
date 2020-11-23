"""
A module for calculating statistics on collaboration networks.
"""

from typing import Any, Iterable, Iterator, Tuple, Optional

import networkx as nx
import community as cm

from pfe.misc.collections import truncate, unique


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
        """Returns the distribution values as a sequence."""

        for k, n in self._p.items():
            while (n := n - 1) >= 0:
                yield k

    def normalized(self) -> dict[int, float]:
        """Returns a normalized distribution."""
        return {k: n / self._n for k, n in self._p.items()}

    def min(self) -> int:
        """Returns the minimum degree."""
        return min(self._p.keys())

    def max(self) -> int:
        """Returns the maximum degree."""
        return max(self._p.keys())

    def mean(self) -> float:
        """Returns the mean value."""
        return sum(k * n for k, n in self._p.items()) / self._n


def publications_per_author(publications: list[dict]) -> Statistic:
    """Computes the distribution of publications per author.

    :param publications: a list of publications (in a raw format).

    :returns: a dictionary representing the distribution.
    """

    authors = {}

    for publication in publications:
        publication_authors = [int(x['id']) for x in publication['authors']]
        publication_authors = unique(publication_authors, lambda x: x)

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


if __name__ == '__main__':
    from pfe.parse_cleaned_data import publications_from
    from pfe.misc.log import timestamped

    domain = 'COMP'
    years = (1990, 1996)
    files = [f'../../../data/{domain}/{domain}-{year}.json'
             for year in range(years[0], years[1] + 1)]

    # Construct a graph.
    publications = publications_from(files, log=timestamped)

    # Calculate a statistic.
    statistic = publications_per_author(publications)
    normalized = statistic.normalized()

    # Print the statistic.
    print()
    print('Degree   Fraction')
    for x, y in sorted(normalized.items(), key=lambda z: z[0]):
        print(f'{x:>6}   {y:.15f}')
