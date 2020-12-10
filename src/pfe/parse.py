"""
Contains functions for constructing graphs from JSON files.
"""

import json
from decimal import Decimal
from pathlib import Path
from typing import Optional, Callable, Union, Tuple, Any

import networkx as nx

from pfe.misc.log import Log, Nothing


def all_publications(between: Tuple[int, int],
                     **kwargs: Any) -> list[dict]:
    """Returns a list of publications in all disciplines between the specified years.

    :param between: a tuple of two integers that specifies the (inclusive) year range.
    :param kwargs: `**kwargs` to pass to `publications_in`.

    :returns: a list of publications.
    """

    directory = Path.cwd()

    # Find the root of the repository.
    while all(x.name != '.gitignore' for x in directory.iterdir()):
        directory = directory.parent

    domains = \
        [x.name for x in (directory / 'data' / 'clean').iterdir()]

    return publications_in(*domains, between=between, **kwargs)


def publications_in(*domains: str,
                    between: Tuple[int, int],
                    **kwargs: Any) -> list[dict]:
    """Returns a list of publications related to the specified domains
    between the specified years.

    In order to find files with corresponding publications, the function
    moves up the current working directory until the root of the repository
    (the directory with `.gitignore`) is found. Then, we assume that
    the repository has the following structure.
    ::

        repo/
        |- data/
           |- clean/
              |- {domain-1}/
                 |- {domain-1}-{year}.json
                 ...
              |- {domain-2}/
                 ...
        |- src/
           ...
        |- .gitignore
        ...

    where {domain-i} is a domain from the provided `domains` and
    {year} is a year in the range as specified by `between`.

    :param domains: a sequence of domain codes ('COMP', 'MATH', 'PHYS', etc.).
    :param between: a tuple of two integers that specifies the (inclusive) year range.
    :param kwargs: `**kwargs` to pass to `publications_from`.

    :returns: a list of publications.
    """

    directory = Path.cwd()

    # Find the root of the repository.
    while all(x.name != '.gitignore' for x in directory.iterdir()):
        directory = directory.parent

    files = [directory / 'data' / 'clean' / domain / f'{domain}-{year}.json'
             for domain in domains
             for year in range(between[0], between[1] + 1)]

    return publications_from(files, **kwargs)


def publications_from(paths: Union[str, list[str]],
                      skip_100: bool = True,
                      where: Optional[Callable] = None,
                      log: Log = Nothing()) -> list[dict]:
    """Returns a list of publications from files specified
    by the provided `paths`.

    :param paths: either a single path or a list of paths
                  to files to read publications from.
    :param skip_100: a flag to consider only publications that have less than
                     100 authors, because it seems that if a publication has
                     100 and more authors, then only 100 of its authors will
                     be present in the list (we, however, assumed that the
                     dataset would not contain such publications at all);
                     thus, the resulting distribution of the number of authors
                     seems to be distorted since there are much more
                     publications with 100 authors than there should have been.
    :param where: a predicate to filter parsed publications.
    :param log: an instance of `Log` to log steps of the execution with.

    :returns: a list of publications.
    """

    if isinstance(paths, (str, Path)):
        paths = [paths]

    publications = []

    def appropriate(publication: dict) -> bool:
        # Skip publications that have 100 authors or more.
        # Refer to the documentation to see why this flag was introduced.
        if skip_100 and len(publication['authors']) >= 100:
            return False

        # Skip publications that do not match a predicate.
        if where is not None and not where(publication):
            return False

        return True

    for path in paths:
        log.info(f'Processing `{path}`...')

        with open(path, 'r') as file:
            data = json.load(file)

        publications += (x for x in data if appropriate(x))

    return publications


def parse(publications: list[dict], into: Optional[nx.Graph] = None) -> nx.Graph:
    """Parses a collaboration network from JSON files and
    constructs a social collaboration graph.

    :param publications: publications represented as dictionaries with JSON.
    :param into: a graph to add parsed nodes and edges into (optional).

    :returns: a constructed social collaboration graph.
    """

    def unique(items: list, select: Callable) -> list:
        unique = set()
        result = list()

        for item in items:
            if (key := select(item)) not in unique:
                unique.add(key)
                result.append(item)

        return result

    graph = into or nx.Graph()

    for publication in publications:
        authors = publication['authors']
        authors = authors if isinstance(authors, list) else [authors]
        authors = unique(authors, lambda x: x['id'])

        # Add nodes.
        for author in authors:
            u = int(author['id'])

            if not graph.has_node(u):
                graph.add_node(u, name=author['name'], weight=0)

            graph.nodes[u]['weight'] += 1

        # Add edges.
        n = len(authors)

        for i in range(n):
            u = int(authors[i]['id'])

            if not graph.has_edge(u, u):
                graph.add_edge(u, u, weight=0)

            # We need to add `1 / (n * 2)` because self-loops are
            # counted twice in a degree.
            graph.edges[u, u]['weight'] += Decimal(1) / Decimal(n * 2)

            for j in range(i + 1, n):
                v = int(authors[j]['id'])

                if not graph.has_edge(u, v):
                    graph.add_edge(u, v, weight=0)

                graph.edges[u, v]['weight'] += Decimal(1) / Decimal(n)

    return graph


if __name__ == '__main__':
    from pfe.misc.log import Pretty, blue

    log: Log = Pretty()
    log.info('Starting...')

    with log.info('Reading a graph...'):
        graph = parse(publications_in('COMP', between=(1990, 1996), log=log))

        log.info(f'Read a graph with '
                 f'{blue | graph.number_of_nodes()} nodes and '
                 f'{blue | graph.number_of_edges()} edges.')
