"""
Calculating and plotting the distribution of
the number of publications per author.
"""

from pfe.misc.log import Log, Pretty, blue
from pfe.misc.plot import Plot
from pfe.parse import publications_in
from pfe.tasks.statistics import publications_per_author


if __name__ == '__main__':
    log: Log = Pretty()
    log.info('Starting...')

    # Reading publications.
    with log.info('Reading publications...'):
        publications = publications_in('COMP', between=(1990, 2018), log=log)

        log.info(f'Read {blue | len(publications)} publications.')

    # Computing the statistic.
    with log.info('Computing the distribution of publications per author...'):
        statistic = publications_per_author(publications)

    # Plot the statistic.
    with log.info('Plotting the distribution...'):
        plot = Plot(tex=True)
        plot.scatter(statistic)

        plot.x.label('Number of Publications')
        plot.x.scale('log')
        plot.x.limit(10 ** -1, 10 ** 4)

        plot.y.label('Number of Authors')
        plot.y.scale('log')
        plot.y.limit(10 ** -1, 10 ** 6)

        plot.save('COMP-ppa.eps')
