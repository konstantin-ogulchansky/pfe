"""
Calculating and plotting the distribution of
the number of communities per publication.
"""

import matplotlib.pyplot as plt

from pfe.misc.log import timestamped
from pfe.misc.plot import Plot
from pfe.parse import parse, publications_from
from pfe.tasks.statistics import communities_per_publication


if __name__ == '__main__':
    log = timestamped
    log('Starting.')

    domain = 'COMP'
    years = (1990, 2018)
    files = [f'../../../../data/clean/{domain}/{domain}-{year}.json'
             for year in range(years[0], years[1] + 1)]

    # Load publications and construct a graph.
    publications = publications_from(files, log=log)
    graph = parse(publications)

    log('Constructed a graph.')

    # Calculate the statistic.
    statistic = communities_per_publication(graph, publications)

    log('Computed the statistic.')

    # Plot the statistic.
    plot = Plot(tex=True)
    plot.scatter(statistic)

    plot.x.label('Number of Communities')

    plot.y.scale('log')
    plot.y.label('Number of Publications')

    plot.save('some-3.eps')
