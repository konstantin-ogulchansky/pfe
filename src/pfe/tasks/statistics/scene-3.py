"""
Calculating and plotting the distribution of
the number of communities per publication.
"""

import matplotlib.pyplot as plt

from pfe.misc.log import timestamped
from pfe.parse_cleaned_data import parse, publications_from
from pfe.tasks.statistics import communities_per_publication


if __name__ == '__main__':
    log = timestamped
    log('Starting.')

    domain = 'COMP'
    years = (1990, 2018)
    files = [f'../../../../data/clean/{domain}/{domain}-{year}.json'
             for year in range(years[0], years[1] + 1)]

    # Load publications and construct a graph.
    publications = publications_from(files, skip_100=True, log=log)
    graph = parse(publications)

    log('Constructed a graph.')

    # Calculate the statistic.
    statistic = communities_per_publication(graph, publications)

    log('Computed the statistic.')

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

    ax.set_yscale('log')

    plt.savefig(f'{domain}-{years[0]}-{years[1]}-cpp.eps')
    plt.show()

    log('Finished.')
