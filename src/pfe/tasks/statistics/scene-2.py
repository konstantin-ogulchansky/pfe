"""
Calculating and plotting the distribution of
the number of authors per publication.
"""

import matplotlib.pyplot as plt

from pfe.parse_cleaned_data import publications_from
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
    publications = publications_from(files, skip_100=True, log=log)

    # Calculate the statistic.
    statistic = authors_per_publication(publications)

    # Print the statistic.
    print()
    print('Authors   Times')
    for x, y in sorted(statistic.items(), key=lambda z: z[0]):
        print(f'{x:>7}   {y:>5}')
    print()

    # Plot the statistic.
    x = statistic.keys()
    y = statistic.values()

    styles = [
        crosses := dict(s=25, color='black', marker='x'),
        circles := dict(s=25, facecolors='none', edgecolors='black'),
    ]

    plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman']})
    plt.rc('text', usetex=True)

    plt.figure()

    ax = plt.gca()
    ax.set_axisbelow(True)
    ax.grid(linestyle='--')
    ax.scatter(x, y, **circles)

    ax.set_xscale('log')
    ax.set_yscale('log')

    ax.set_xlim(10 ** -1, 10 ** 4)
    ax.set_ylim(10 ** -1, 10 ** 5)

    plt.savefig(f'{domain}-{years[0]}-{years[1]}-app.eps')
    plt.show()

    log('Finished.')
