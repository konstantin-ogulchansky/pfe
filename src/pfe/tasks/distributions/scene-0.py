"""
Compute different metrics, such as
    - the number of authors,
    - the number of publications,
    - the number of collaborations (unweighted, weighted).
"""

from pfe.misc.log import Log, Pretty
from pfe.misc.style import blue
from pfe.parse import parse, publications_in
from pfe.tasks.distributions import number_of_authors, number_of_publications, number_of_collaborations


if __name__ == '__main__':
    log: Log = Pretty()
    log.info('Starting.')

    with log.scope.info('Reading publications.'):
        publications = list(publications_in('COMP', between=(1990, 1996), log=log))

    with log.scope.info('Constructing a graph.'):
        graph = parse(publications)

        log.info(f'Constructed a graph with '
                 f'{blue | graph.number_of_nodes()} nodes and '
                 f'{blue | graph.number_of_edges()} edges.')

    with log.scope.info('Computing the metrics.'):
        log.info('The number of authors:                   '
                 + str(blue | number_of_authors(publications)))
        log.info('The number of publications:              '
                 + str(blue | number_of_publications(publications)))
        log.info('The number of unweighted collaborations: '
                 + str(blue | number_of_collaborations(graph)))
        log.info('The number of weighted collaborations:   '
                 + str(blue | number_of_collaborations(graph, weighted=True)))