"""
...
"""

import matplotlib.pyplot as plt

from pfe.misc.log import timestamped
from pfe.parse_cleaned_data import publications_from, parse
from pfe.tasks.hypothesis import degree_distribution


if __name__ == '__main__':
    log = timestamped
    log('Starting...')

    domain = 'COMP'
    years = (1990, 2018)
    files = [f'../../../../data/clean/{domain}/{domain}-{year}.json'
             for year in range(years[0], years[1] + 1)]

    # Construct a graph.
    graph = parse(publications_from(files, skip_100=True, log=log))

    log(f'Read a graph with '
        f'{graph.number_of_nodes()} nodes and '
        f'{graph.number_of_edges()} edges.')

    # Compute the "original" (not truncated) degree distribution.
    original = degree_distribution(graph)
    original_normalized = original.normalized()

    # Plot the data.
    styles = [
        crosses := dict(s=25, color='black', marker='x'),
        circles := dict(s=25, facecolors='none', edgecolors='black'),
    ]

    plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman']})
    plt.rc('text', usetex=True)

    fig, ax = plt.subplots()

    ax.grid(linestyle='--')
    ax.set_axisbelow(True)

    ax.scatter(original.keys(), original.values(), **circles)

    ax.set_xscale('log')
    ax.set_yscale('log')

    ax.set_xlim(10 ** -1, 10 ** 4)
    ax.set_ylim(10 ** -1, 10 ** 5)

    plt.savefig('some-1.eps')
    plt.show()
