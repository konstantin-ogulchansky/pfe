"""
Contains functions for constructing graphs from JSON files.
"""

import json
from typing import Optional, Callable, Any, Union

import networkx as nx

from pfe.misc.collections import unique


def parse(paths: Union[str, list[str]],
          where: Optional[Callable[[dict], bool]] = None,
          into: Optional[nx.Graph] = None,
          limit: Optional[int] = None,
          log: Optional[Callable] = None) -> nx.Graph:
    """Parses a collaboration network from JSON files and
    constructs a social collaboration graph.

    :param paths: paths to JSON files with publications.
    :param where: a predicate to filter parsed publications.
    :param into: a graph to parse publications into (optional).
    :param limit: limits the number of publications
                  to construct a graph from.
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

    if log is None:
        log = lambda *args, **kwargs: ...  # Do nothing.

    graph = into or nx.Graph()

    if not isinstance(paths, list):
        paths = [paths]

    # Parse all files with publications.
    for path in paths:
        with open(path, 'r') as file:
            data = file.read()
            data = json.loads(data)

        publications = data['search-results']['entry']

        log(f'Processing `{path}` ({len(publications)} publications).')

        # Parse all publications in a file.
        for publication in publications:
            if not appropriate(publication):
                continue

            # Consider only `limit` publications.
            if limit is not None and (limit := limit - 1) < 0:
                break

            authors = publication['author']
            authors = unique(authors, lambda x: x['authid'])

            # Do not consider publications with a single unique author.
            if len(authors) <= 1:
                continue

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
    """Returns a predicate of a publication that returns `True` if
    a publication is affiliated to `city` and `False` otherwise.

    Note: a publication is affiliated to `city` if there exist a coauthor
          of this publication that is affiliated to `city`.

    :param city: a city for publications to be affiliated to.

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


def with_no_more_than(number: int, what: str) -> Callable[[dict], bool]:
    """..."""

    if what == 'authors':
        def where(publication: dict[str, Any]) -> bool:
            return len(publication['author']) <= number

    try:
        where
    except NameError:
        raise ValueError(f'Invalid `what` value "{what}": '
                         f'please see the documentation.')

    return where


if __name__ == '__main__':
    import matplotlib.pyplot as plt

    import pfe.misc.log

    publications = [f'../../data/json/COMP-{year}.json' for year in range(1990, 1996 + 1)]
    graph = parse(publications, with_no_more_than(100, 'authors'),
                  log=pfe.misc.log.timestamped)

    print('Names:', len({node['name'] for _, node in graph.nodes(data=True)}))
    print('Nodes:', graph.number_of_nodes())
    print('Edges:', graph.number_of_edges())

    nx.draw(graph)
    plt.show()
