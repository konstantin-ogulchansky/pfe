"""
Compute different metrics, such as
    - the number of authors,
    - the number of publications,
    - the number of collaborations (unweighted, weighted).
"""

import networkx as nx

from pfe.misc.log import Log, Pretty
from pfe.misc.style import blue
from pfe.parse import parse, all_publications, publications_in


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


if __name__ == '__main__':
    log: Log = Pretty()
    log.info('Starting...')

    with log.info('Reading publications.'):
        publications = all_publications(between=(1990, 2018), log=log)

    with log.info('Constructing a graph.'):
        graph = parse(publications)

        log.info(f'Constructed a graph with '
                 f'{blue | graph.number_of_nodes()} nodes and '
                 f'{blue | graph.number_of_edges()} edges.')

    with log.info('Computing the metrics.'):
        log.info('The number of authors:                   '
                 + str(blue | number_of_authors(publications)))
        log.info('The number of publications:              '
                 + str(blue | number_of_publications(publications)))
        log.info('The number of unweighted collaborations: '
                 + str(blue | number_of_collaborations(graph)))
        log.info('The number of weighted collaborations:   '
                 + str(blue | number_of_collaborations(graph, weighted=True)))
