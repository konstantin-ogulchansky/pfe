"""
Calculating and plotting the distribution of
the number of communities per publication.
"""

from pfe.misc.log import Log, Pretty, blue
from pfe.misc.plot import Plot
from pfe.parse import parse, publications_in
from pfe.tasks.statistics import communities_per_publication


if __name__ == '__main__':
    log: Log = Pretty()
    log.info('Starting...')

    # Reading publications.
    with log.info('Reading publications...'):
        publications = publications_in('COMP', between=(1990, 2018), log=log)

        log.info(f'Read {blue | len(publications)} publications.')

    # Constructing a graph.
    with log.info('Constructing a graph...'):
        graph = parse(publications)

        log.info(f'Constructed a graph with '
                 f'{blue | graph.number_of_nodes()} nodes and '
                 f'{blue | graph.number_of_edges()} edges.')

    # Compute the statistic.
    with log.info('Computing the distribution of communities per publication...'):
        statistic = communities_per_publication(graph, publications)

    # Plot the statistic.
    with log.info('Plotting the distribution...'):
        plot = Plot(tex=True)
        plot.scatter(statistic)
        plot.draw(statistic)

        plot.x.label('Number of Communities')

        plot.y.label('Number of Publications')
        plot.y.scale('log')

        plot.save('COMP-cpp.eps')
