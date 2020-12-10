"""
...
"""

import json
from pathlib import Path

import igraph as ig

from pfe.misc.log import Log, Pretty
from pfe.misc.style import blue, underlined

if __name__ == '__main__':
    log: Log = Pretty()
    log.info('Starting...')

    data = Path('../../data/graph')

    with log.info('Reading `ig.Graph`...'):
        graph = ig.Graph.Read_Pajek(str(data / 'ig_full_graph_relabeled_nodes.net'))

        log.info(f'Read a graph with '
                 f'{blue | len(graph.vs)} vertices and '
                 f'{blue | len(graph.es)} edges.')

    with log.info(f'Detecting communities using the {underlined | "Leiden"} method...'):
        objective = 'modularity'
        communities = graph.community_leiden(objective_function=objective, weights='weight')

        log.info('The objective:               ' + objective)
        log.info('The number of communities:   ' + str(blue | len(communities)))
        log.info('The modularity value:        ' + str(blue | communities.modularity))

    with log.info('Saving communities into a file...'):
        with open(data / 'leiden_communities.json', 'w') as file:
            json.dump(dict(enumerate(communities)), file)

    with log.info('Saving the modularity value into a file...'):
        with open(data / 'leiden_modularity.json', 'w') as file:
            json.dump(communities.modularity, file)
