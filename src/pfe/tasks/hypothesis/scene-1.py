"""
...
"""

from pfe.misc.log import timestamped
from pfe.misc.plot import Plot
from pfe.parse import publications_from, parse
from pfe.tasks.hypothesis import degree_distribution


if __name__ == '__main__':
    log = timestamped
    log('Starting...')

    domain = 'COMP'
    years = (1990, 2018)
    files = [f'../../../../data/clean/{domain}/{domain}-{year}.json'
             for year in range(years[0], years[1] + 1)]

    # Construct a graph.
    graph = parse(publications_from(files, log=log))

    log(f'Read a graph with '
        f'{graph.number_of_nodes()} nodes and '
        f'{graph.number_of_edges()} edges.')

    # Compute the "original" (not truncated) degree distribution.
    original = degree_distribution(graph)
    original_normalized = original.normalized()

    # Plot the data.
    plot = Plot(tex=True)
    plot.scatter(original)

    plot.x.scale('log')
    plot.x.limit(10 ** -1, 10 ** 4)
    plot.x.label('x')

    plot.y.scale('log')
    plot.y.limit(10 ** -1, 10 ** 5)
    plot.y.label('y')

    plot.save('some-1.eps')
