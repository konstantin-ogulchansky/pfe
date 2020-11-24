"""
Calculating and plotting the distribution of
the number of publications per author.
"""

from pfe.misc.plot import Plot
from pfe.misc.log import timestamped
from pfe.parse import publications_from
from pfe.tasks.statistics import publications_per_author


if __name__ == '__main__':
    log = timestamped
    log('Starting.')

    domain = 'COMP'
    years = (1990, 2018)
    files = [f'../../../../data/clean/{domain}/{domain}-{year}.json'
             for year in range(years[0], years[1] + 1)]

    # Construct a graph.
    publications = publications_from(files, log=log)

    # Calculate the statistic.
    statistic = publications_per_author(publications)

    # Plot the statistic.
    plot = Plot(tex=True)
    plot.scatter(statistic)

    plot.x.scale('log')
    plot.x.limit(10 ** -1, 10 ** 4)
    plot.x.label('Number of Publications')

    plot.y.scale('log')
    plot.y.limit(10 ** -1, 10 ** 6)
    plot.y.label('Number of Authors')

    plot.save('some-1.eps')
