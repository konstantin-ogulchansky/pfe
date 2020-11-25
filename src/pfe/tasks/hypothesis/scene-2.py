"""
Plot the weighted degree distribution.
"""

from pfe.misc.log import timestamped
from pfe.misc.plot import Plot
from pfe.parse import parse, publications_in
from pfe.tasks.hypothesis import degree_distribution


if __name__ == '__main__':
    log = timestamped
    log('Starting...')

    # Construct a graph.
    graph = parse(publications_in('COMP', between=(1990, 2018), log=log))

    log(f'Read a graph with '
        f'{graph.number_of_nodes()} nodes and '
        f'{graph.number_of_edges()} edges.')

    # Compute the weighted degree distribution.
    statistic = degree_distribution(graph, weighted=True)

    # Plot the data.
    plot = Plot(tex=True)
    plot.scatter(statistic)

    plot.x.scale('log')
    plot.x.limit(10 ** -1, 10 ** 4)
    plot.x.label('Weighted Degree $k$')

    plot.y.scale('log')
    plot.y.limit(10 ** -1, 10 ** 5)
    plot.y.label('$P_w(k)$')

    plot.save('some-2.eps')
