"""
Calculating and plotting the distribution of
the number of authors per publication.
"""

from pfe.misc.log import timestamped
from pfe.misc.plot import Plot
from pfe.parse import publications_in
from pfe.tasks.statistics import authors_per_publication


if __name__ == '__main__':
    log = timestamped
    log('Starting.')

    # Load publications.
    publications = publications_in('COMP', between=(1990, 2018), log=log)

    # Calculate the statistic.
    statistic = authors_per_publication(publications)

    # Print the statistic.
    print()
    print('Authors   Times')
    for x, y in sorted(statistic.items(), key=lambda z: z[0]):
        print(f'{x:>7}   {y:>5}')
    print()

    # Plot the statistic.
    plot = Plot(tex=True)
    plot.scatter(statistic)

    plot.x.label('Number of Authors')
    plot.x.scale('log')
    plot.x.limit(10 ** -1, 10 ** 4)

    plot.y.label('Number of Publications')
    plot.y.scale('log')
    plot.y.limit(10 ** -1, 10 ** 5)

    plot.save('some-2.eps')
