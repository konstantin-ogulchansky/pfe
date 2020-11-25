"""
Contains functions for constructing graphs from JSON files.
"""

import json
from pathlib import Path
from typing import Optional, Callable, Union, Tuple, Any

import networkx as nx

from pfe.misc.collections import unique
from pfe.misc.log import nothing


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
    :param between: a tuple of two integers that specifies the (inclusive) range

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
                      log: Optional[Callable] = nothing,
                      skip_100: bool = True) -> list[dict]:
    """Returns a list of publications from files specified
    by the provided `paths`.

    :param paths: either a single path or a list of paths
                  to files to read publications from.
    :param log: a function to log steps of the execution with.
    :param skip_100: a flag to consider only publications that have less than
                     100 authors, because it seems that if a publication has
                     100 and more authors, then only 100 of its authors will
                     be present in the list (we, however, assumed that the
                     dataset would not contain such publications at all);
                     thus, the resulting distribution of the number of authors
                     seems to be distorted since there are much more
                     publications with 100 authors than there should have been.

    :returns: a list of publications.
    """

    if isinstance(paths, (str, Path)):
        paths = [paths]

    publications = []

    for path in paths:
        log(f'Processing `{path}`...')

        with open(path, 'r') as file:
            data = json.load(file)

        # Refer to the documentation to see why this flag was introduced.
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

    graph = parse(publications_in('COMP', between=(1990, 2018), log=timestamped))

    print()
    print('Unique names:', len({node['name'] for _, node in graph.nodes(data=True)}))
    print('Nodes:', graph.number_of_nodes())
    print('Edges:', graph.number_of_edges())
