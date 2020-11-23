"""
Calculating and plotting the distribution of
the number of publications per author.
"""

import matplotlib.pyplot as plt

from pfe.parse import parse
from pfe.misc.log import timestamped
from pfe.tasks.statistics import publications_per_author


if __name__ == '__main__':
    log = timestamped
    log('Starting.')

    years = (1990, 2018)
    domain = 'COMP'
    publications = [f'../../../../data/raw/{domain}/{domain}-{year}.json'
                    for year in range(years[0], years[1] + 1)]

    # Construct a graph.
    graph = parse(publications, log=log)

    # Calculate the statistic.
    statistic = publications_per_author(graph)

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

    plt.savefig(f'{domain}-{years[0]}-{years[1]}-ppa.eps')
    plt.show()

    log('Finished.')
