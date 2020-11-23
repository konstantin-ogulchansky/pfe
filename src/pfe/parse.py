"""
Contains functions for constructing graphs from JSON files.
"""

import json
from typing import Optional, Callable, Any, Union

import networkx as nx

from pfe.misc.collections import unique
from pfe.misc.log import nothing


def parse(paths: Union[str, list[str]],
          where: Optional[Callable[[dict], bool]] = None,
          limit: Optional[int] = None,
          into: Optional[nx.Graph] = None,
          log: Optional[Callable] = nothing) -> nx.Graph:
    """Parses a collaboration network from JSON files and
    constructs a social collaboration graph.

    :param paths: paths to JSON files with publications.
    :param where: a predicate to filter parsed publications.
    :param limit: limits the number of publications to construct a graph from.
    :param into: a graph to add parsed nodes and edges into (optional).
    :param log: called to log steps of the execution.

    :returns: a constructed social collaboration graph.
    """

    def appropriate(publication: dict) -> bool:
        # Skip publications without affiliation.
        if 'affiliation' not in publication:
            return False
        # Skip publications without authors.
        if 'author' not in publication:
            return False

        authors = publication['author']

        # Skip publications without at least two authors.
        if not isinstance(authors, list):
            return False
        if len(authors) <= 1:
            return False

        # Skip publications that do not match a predicate.
        if where is not None and not where(publication):
            return False

        return True

    graph = into if into is not None else nx.Graph()

    if not isinstance(paths, list):
        paths = [paths]

    # Parse all files with publications.
    for path in paths:
        with open(path, 'r') as file:
            data = json.load(file)

        publications = data['search-results']['entry']

        log(f'Processing `{path}` ({len(publications)} publications).')

        # Parse all publications in a file.
        for publication in publications:
            if not appropriate(publication):
                continue

            authors = publication['author']
            authors = unique(authors, lambda x: x['authid'])

            # Do not consider publications with a single unique author.
            if len(authors) <= 1:
                continue

            # Consider only `limit` publications.
            if limit is not None and (limit := limit - 1) < 0:
                break

            # Add nodes.
            for author in authors:
                u = int(author['authid'])

                if not graph.has_node(u):
                    graph.add_node(u, name=author['authname'])

            # Add edges.
            for i in range(len(authors)):
                for j in range(i + 1, len(authors)):
                    u = int(authors[i]['authid'])
                    v = int(authors[j]['authid'])

                    if not graph.has_edge(u, v):
                        graph.add_edge(u, v, weight=1)
                    else:
                        graph[u][v]['weight'] += 1

        log(f'Processed `{path}`.')

    return graph


def affiliated_to(city: str) -> Callable[[dict], bool]:
    """Returns a predicate for a publication that returns `True` if
    a publication is affiliated to `city` and `False` otherwise.

    Note: a publication is affiliated to `city` if there exist a coauthor
          of this publication that is affiliated to `city`.

    :param city: a city that publications should be affiliated to.

    :returns: a predicate.
    """

    def where(publication: dict[str, Any]) -> bool:
        if not (affiliation := publication['affiliation']):
            return False

        if isinstance(affiliation, list):
            return any(x['affiliation-city'] == city
                       for x in affiliation)
        else:
            return affiliation['affiliation-city'] == city

    return where


def with_no_more_than(number: int, what: Callable[[dict], int]) -> Callable[[dict], bool]:
    """Returns a predicate for a publication that checks whether
    a property specified in `what` is less or equal to `number`.
    ::

        what(publication) <= number

    :param number: a number to compare with.
    :param what: a function that returns a value that
                 should be less than `number`.

    :returns: a predicate.
    """

    def where(publication: dict[str, Any]) -> bool:
        return what(publication) <= number

    return where


def authors(publication: dict[str, Any]) -> int:
    """Returns the number of authors of a publication."""
    return len(unique(publication['author'], lambda x: x['authid']))


if __name__ == '__main__':
    from pfe.misc.log import timestamped

    years = (1990, 2018)
    domain = 'COMP'
    publications = [f'../../../data/{domain}/{domain}-{year}.json'
                    for year in range(years[0], years[1] + 1)]

    graph = parse(publications, with_no_more_than(50, authors),
                  log=timestamped)

    print()
    print('Unique names:', len({node['name'] for _, node in graph.nodes(data=True)}))
    print('Nodes:', graph.number_of_nodes())
    print('Edges:', graph.number_of_edges())
