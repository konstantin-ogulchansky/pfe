"""
Calculating and plotting the distribution of
the number of authors per publication.
"""

import matplotlib.pyplot as plt

from pfe.misc.plot import Plot
from pfe.parse import publications_from
from pfe.tasks.statistics import authors_per_publication
from pfe.misc.log import timestamped


if __name__ == '__main__':
    log = timestamped
    log('Starting.')

    domain = 'COMP'
    years = (1990, 2018)
    files = [f'../../../../data/clean/{domain}/{domain}-{year}.json'
             for year in range(years[0], years[1] + 1)]

    # Load publications.
    publications = publications_from(files, log=log)

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

    plot.x.scale('log')
    plot.x.limit(10 ** -1, 10 ** 4)
    plot.x.label('Number of Authors')

    plot.y.scale('log')
    plot.y.limit(10 ** -1, 10 ** 5)
    plot.y.label('Number of Publications')

    plot.save('some-2.eps')
