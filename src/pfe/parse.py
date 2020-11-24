"""
Contains functions for constructing graphs from JSON files.
"""

import json
from typing import Optional, Callable, Union

import networkx as nx

from pfe.misc.collections import unique
from pfe.misc.log import nothing


def publications_from(paths: Union[str, list[str]],
                      skip_100: bool = True,
                      log: Optional[Callable] = nothing) -> list[dict]:
    """TODO."""

    if isinstance(paths, str):
        paths = [paths]

    publications = []

    for path in paths:
        log(f'Processing `{path}`...')

        with open(path, 'r') as file:
            data = json.load(file)

        # We consider only publications that have less than 100 authors,
        # because it seems that if a publication has 100 and more authors,
        # then only 100 of its authors will be present in the list
        # (we, however, assumed that the dataset would not contain such
        # publications at all). Thus, the resulting distribution seems
        # to be distorted since there are much more publications with
        # 100 authors than there should have been.
        if skip_100:
            publications += (x for x in data if len(x['authors']) < 100)
        else:
            publications += data

    return publications


def parse(publications: list[dict],
          where: Optional[Callable[[dict], bool]] = None,
          into: Optional[nx.Graph] = None) -> nx.Graph:
    """Parses a collaboration network from JSON files and
    constructs a social collaboration graph.

    :param publications: publications represented as dictionaries with JSON.
    :param where: a predicate to filter parsed publications.
    :param into: a graph to add parsed nodes and edges into (optional).

    :returns: a constructed social collaboration graph.
    """

    def appropriate(publication: dict) -> bool:
        # Skip publications without authors.
        if 'authors' not in publication:
            return False
        # Skip publications without affiliation.
        if all(author['affiliation_id'] is None for author in publication['authors']):
            return False

        authors = publication['authors']

        # Skip publications without at least two authors.
        if not isinstance(authors, list):
            return False
        if len(authors) <= 1:
            return False

        # Skip publications that do not match a predicate.
        if where is not None and not where(publication):
            return False

        return True

    graph = into or nx.Graph()

    for publication in publications:
        if not appropriate(publication):
            continue

        authors = publication['authors']
        authors = unique(authors, lambda x: x['id'])

        # Do not consider publications with a single unique author.
        if len(authors) <= 1:
            continue

        # Add nodes.
        for author in authors:
            u = int(author['id'])

            if not graph.has_node(u):
                graph.add_node(u, name=author['name'])

        # Add edges.
        for i in range(len(authors)):
            for j in range(i + 1, len(authors)):
                u = int(authors[i]['id'])
                v = int(authors[j]['id'])

                if not graph.has_edge(u, v):
                    graph.add_edge(u, v, weight=1)
                else:
                    graph[u][v]['weight'] += 1

    return graph


if __name__ == '__main__':
    from pfe.misc.log import timestamped

    domain = 'COMP'
    years = (1990, 2018)
    files = [f'../../data/clean/{domain}/{domain}-{year}.json'
             for year in range(years[0], years[1] + 1)]

    graph = parse(publications_from(files, log=timestamped))

    print()
    print('Unique names:', len({node['name'] for _, node in graph.nodes(data=True)}))
    print('Nodes:', graph.number_of_nodes())
    print('Edges:', graph.number_of_edges())
