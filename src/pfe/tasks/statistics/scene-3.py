"""
Calculating and plotting the distribution of
the number of communities per publication.
"""

from pfe.misc.log import timestamped
from pfe.misc.plot import Plot
from pfe.parse import parse, publications_in
from pfe.tasks.statistics import communities_per_publication


if __name__ == '__main__':
    log = timestamped
    log('Starting.')

    # Load publications and construct a graph.
    publications = publications_in('COMP', between=(1990, 2018), log=log)
    graph = parse(publications)

    log('Constructed a graph.')

    # Calculate the statistic.
    statistic = communities_per_publication(graph, publications)

    log('Computed the statistic.')

    # Plot the statistic.
    plot = Plot(tex=True)
    plot.scatter(statistic)
    plot.draw(statistic)

    plot.x.label('Number of Communities')

    plot.y.label('Number of Publications')
    plot.y.scale('log')

    plot.save('some-3.eps')
