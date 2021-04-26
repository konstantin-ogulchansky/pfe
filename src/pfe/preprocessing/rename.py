"""
Saving a renamed graph to a file.
"""

import csv
from pathlib import Path

import networkx as nx

from pfe.misc.log import Pretty
from pfe.parse import parse, all_publications, publications_in

# if __name__ == '__main__':
def remane(data: Path, file: Path, common):
    log = Pretty()
    log.info('Starting.')

    # data = Path('../../../data/graph')
    # data = Path('../matrices/test-data/COMP-data')

    # Reading a graph.
    # if (data / 'nx_comp_nice_all_float_graph.txt').is_file():
    #     with log.scope.info('Reading a graph from cache.'):
    #         graph = nx.read_weighted_edgelist(data / 'nx_comp_nice_all_int_graph.txt')
    if (data / file).is_file():
        with log.scope.info('Reading a graph from cache.'):
            graph = nx.read_weighted_edgelist(data / file)
    # else:
    #     with log.scope.info('Reading a graph from JSON files.'):
    #         # graph = parse(all_publications(between=(1990, 2018), log=log))
    #         graph = parse(publications_in('COMP', between=(1990, 2018), log=log))

    log.info(f'Read a graph with '
             f'{graph.number_of_nodes()} nodes and '
             f'{graph.number_of_edges()} edges.')

    # Rename nodes and save the graph to a file
    # to be able to read `igraph` faster.
    with log.scope.info('Renaming nodes.'):
        mapping = zip(graph.nodes, range(1, len(graph.nodes)+1))
        mapping = dict(mapping)

        graph = nx.relabel_nodes(graph, mapping, copy=False)

    with log.scope.info('Saving the mapping to a file.'):
        with open(data / f'nx_node_mapping_{common}.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(mapping.items())

    # Save the renamed graph to a file.
    with log.scope.info('Saving the `nx` graph to a file.'):
        filename = f'nx_{common}_graph'+'_relabeled_nodes.txt'
        nx.write_weighted_edgelist(graph, data / filename)

    with log.scope.info('Saving the `ig` graph to a file.'):
        encoding = 'utf-8'
        with open(data / f'ig_{common}_graph.net', 'wb') as f:
            f.write(f'*Vertices {len(graph.nodes())}\n'.encode(encoding))
            f.write('*Edges\n'.encode(encoding))
            nx.write_weighted_edgelist(graph, f, encoding=encoding)


if __name__ == '__main__':
    from pfe.misc.log import Pretty
    from pfe.misc.style import blue

    log = Pretty()
    log.info('Starting.')
    for year in range(1990, 2018 +1):
        data = Path('../matrices/test-data/COMP-data/graph/nice/by_year/int')

        file = Path(f'nx_comp_nice_{year}_int_graph.txt')
        common_part = f'comp_nice_{year}_int'
        remane(data, file, common_part)
