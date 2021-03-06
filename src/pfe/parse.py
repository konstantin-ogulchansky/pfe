"""
Contains functions for constructing graphs from JSON files.
"""

import json
from decimal import Decimal
from pathlib import Path
from typing import Optional, Callable, Union, Tuple, Any, Iterable, List

import networkx as nx

from pfe.misc.log import Log, Nothing
from pfe.misc.log.misc import percents
from pfe.misc.style import magenta


def all_publications(between: Tuple[int, int],
                     **kwargs: Any) -> Iterable[dict]:
    """Returns a list of publications in all disciplines between the specified years.

    :param between: a tuple of two integers that specifies the (inclusive) year range.
    :param kwargs: `**kwargs` to pass to `publications_in`.

    :return: a list of publications.
    """

    directory = Path.cwd()

    # Find the root of the repository.
    while all(x.name != '.gitignore' for x in directory.iterdir()):
        directory = directory.parent

    domains = \
        (x.name for x in (directory / 'data' / 'clean').iterdir())

    return publications_in(*domains, between=between, **kwargs)


def publications_in(*domains: str,
                    between: Tuple[int, int],
                    **kwargs: Any) -> Iterable[dict]:
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

    Here {domain-i} is a domain from the provided `domains` and
    {year} is a year in the range as specified by `between`.

    :param domains: a sequence of domain codes ('COMP', 'MATH', 'PHYS', etc.).
    :param between: a tuple of two integers that specifies the (inclusive) year range.
    :param kwargs: `**kwargs` to pass to `publications_from`.

    :return: a list of publications.
    """

    directory = Path.cwd()

    # Find the root of the repository.
    while all(x.name != '.gitignore' for x in directory.iterdir()):
        directory = directory.parent

    files = [directory / 'data' / 'clean' / domain / f'{domain}-{year}.json'
             for domain in domains
             for year in range(between[0], between[1] + 1)]

    return publications_from(files, **kwargs)


def publications_from(paths: Union[str, List[str]],
                      skip_100: bool = True,
                      where: Optional[Callable] = None,
                      log: Log = Nothing()) -> Iterable[dict]:
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

    :return: a list of publications.
    """

    if isinstance(paths, (str, Path)):
        paths = [paths]

    def appropriate(publication: dict) -> bool:
        # Skip publications that have 100 authors or more.
        # Refer to the documentation to see why this flag was introduced.
        if skip_100 and len(publication['authors']) >= 100:
            return False

        # Skip publications that do not match a predicate.
        if where is not None and not where(publication):
            return False

        return True

    for i, path in enumerate(paths, start=1):
        log.info(f'Reading "{magenta | path.name}". [{percents(i, len(paths))}]')

        with open(path, 'r') as file:
            publications = json.load(file)

        for publication in publications:
            if appropriate(publication):
                yield publication


def parse(publications: Iterable[dict], self_loops: bool = True, to: Optional[nx.Graph] = None) -> nx.Graph:
    """Parses a collaboration network from JSON files and
    constructs a collaboration graph.

    TODO:
        - Describe how publications are parsed.
        - Describe how attributes are assigned.

    :param publications: publications represented as dictionaries with JSON.
    :param self_loops: whether to add self-loops to the graph.
    :param to: a graph to add parsed nodes and edges to (optional).

    :return: the constructed collaboration graph.
    """

    def unique(items: list, select: Callable) -> list:
        unique = set()
        result = list()

        for item in items:
            if (key := select(item)) not in unique:
                unique.add(key)
                result.append(item)

        return result

    graph = to if to is not None else nx.Graph()
    labex = []
    with open("C:/Users/2shel/Desktop/Labex.json", 'r', encoding='UTF-8') as file:
        labex_publications = json.load(file)

    for lp in labex_publications:
        labex += lp['ids'].keys()

    for publication in publications:
        authors = publication['authors']
        authors = authors if isinstance(authors, list) else [authors]
        authors = unique(authors, lambda x: x['id'])

        # Add nodes.
        for author in authors:
            u = int(author['id'])

            if not graph.has_node(u):
                graph.add_node(u, name=author['name'], publications=0)
                if author['id'] in labex:
                    graph.nodes[u]['labex'] = 1

            graph.nodes[u]['publications'] += 1

        # Add edges.
        for i in range(n := len(authors)):
            u = int(authors[i]['id'])

            if self_loops:
                if not graph.has_edge(u, u):
                    graph.add_edge(u, u, weight=0, collaborations=0)

                # We need to add `1 / (n * 2)` because self-loops are
                # counted twice in a degree.
                graph.edges[u, u]['weight'] += Decimal(1) / Decimal(n * 2)
                graph.edges[u, u]['collaborations'] += 1

            for j in range(i + 1, n):
                v = int(authors[j]['id'])

                if not graph.has_edge(u, v):
                    graph.add_edge(u, v, weight=0, collaborations=0)

                # graph.edges[u, v]['weight'] += float(Decimal(1) / Decimal(n - 1 + self_loops))
                graph.edges[u, v]['weight'] += 1
                graph.edges[u, v]['collaborations'] += 1

    return graph


if __name__ == '__main__':
    from pfe.misc.log import Pretty
    from pfe.misc.style import blue

    path = Path('matrices/test-data/COMP-data/graph/full_comp/int_by_year')

    log = Pretty()
    with log.scope.info('Starting.'):
        # for year in range(2013, 2016):
        #
        #     graph = parse(all_publications(between=(1990, year), log=log))
        #     nx.write_graphml(graph, path / Path(f'nx_int_graph_{year}.xml'))

        for year in range(1990, 2018 +1):

            with log.scope.info('Reading a graph.'):
                graph = parse(publications_in('COMP', between=(1990, year), log=log), self_loops=False)

                log.info(f'Read a graph with '
                         f'{blue | graph.number_of_nodes()} nodes and '
                         f'{blue | graph.number_of_edges()} edges.')

                with open(path / 'graph.log', 'a+') as log_file:
                    log_file.write(f'Graph {1990, year}: '
                                   f'{graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges.\n')

            nx.write_graphml(graph, path / Path(f'nx_comp_{year}_int_graph.xml'))
