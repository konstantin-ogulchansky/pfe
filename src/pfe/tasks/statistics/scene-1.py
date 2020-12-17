"""
Calculating and plotting the distribution of
the number of publications per author.
"""

from pfe.misc.log import Log, Pretty, redirect_stderr_to
from pfe.misc.plot import Plot
from pfe.misc.style import blue
from pfe.parse import publications_in
from pfe.tasks.statistics import publications_per_author


if __name__ == '__main__':
    log: Log = Pretty()
    log.info('Starting...')

    redirect_stderr_to(log.warn)

    with log.scope.info('Reading publications.'):
        publications = publications_in('COMP', between=(1990, 2018), log=log)
        publications = list(publications)

        log.info(f'Read {blue | len(publications)} publications.')

    with log.scope.info('Computing the distribution of publications per author.'):
        statistic = publications_per_author(publications)

    with log.scope.info('Plotting the distribution.'):
        plot = Plot(tex=True)
        plot.scatter(statistic)

        plot.x.label('Number of Publications')
        plot.x.scale('log')
        plot.x.limit(10 ** -1, 10 ** 4)

        plot.y.label('Number of Authors')
        plot.y.scale('log')
        plot.y.limit(10 ** -1, 10 ** 6)

        plot.save('COMP-ppa.eps')
