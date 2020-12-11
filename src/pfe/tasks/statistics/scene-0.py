"""
Compute different metrics, such as
    - the number of authors,
    - the number of publications,
    - the number of collaborations (unweighted, weighted).
"""

from pfe.misc.log import Log, Pretty
from pfe.misc.style import blue
from pfe.parse import parse, all_publications, publications_in
from pfe.tasks.statistics import number_of_authors, number_of_publications, number_of_collaborations


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
