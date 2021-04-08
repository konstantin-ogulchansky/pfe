import csv
import json
from pathlib import Path
import igraph as ig
from pfe.misc.log import Pretty, Log
from pfe.misc.style import blue, underlined
from pfe.parse import publications_in

data = Path('test-data/COMP-data')
new_data = Path('test-data/COMP-data')


def create_data():
    log: Log = Pretty()

    with log.scope.info('Reading `ig.Graph`...'):
        # graph = ig.Graph.Read_Pajek(str(data / 'ig_full_graph_relabeled_nodes.net'))
        graph = ig.Graph.Read_Pajek(str(data / 'ig_comp_graph_relabeled_nodes.net'))

        log.info(f'Read a graph with '
                 f'{blue | len(graph.vs)} vertices and '
                 f'{blue | len(graph.es)} edges.')

    graph = graph.clusters().giant()

    with log.scope.info(f'Detecting communities using the {underlined | "Leiden"} method...'):
        objective = 'modularity'
        communities = graph.community_leiden(objective_function=objective, weights='weight')

        log.info('The objective:               ' + objective)
        log.info('The number of communities:   ' + str(blue | len(communities)))
        log.info('The modularity value:        ' + str(blue | communities.modularity))

    with log.scope.info('Saving communities into a file...'):
        with open(new_data / 'leiden_communities.json', 'w') as file:
            json.dump(dict(enumerate(communities)), file)

    with log.scope.info('Saving the modularity value into a file...'):
        with open(new_data / 'leiden_modularity.json', 'w') as file:
            json.dump(communities.modularity, file)

    communities = dict(enumerate(communities))
    new_dict = {}

    for k_community, v_authors in communities.items():
        for author in v_authors:
            new_dict[int(author)] = k_community

    communities = new_dict

    with log.scope.info('Saving author-community into a file...'):
        with open(new_data / 'leiden_author-community.json', 'w') as file:
            json.dump(communities, file)

    with log.scope.info('Reading authors-communities.'):
        with open(new_data / 'leiden_author-community.json', 'r') as file:
            communities = json.load(file)

    mapping = {}
    # with open(data / 'nx_node_mapping.csv', 'r') as file:
    with open(new_data / 'nx_node_mapping.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            mapping[row[0]] = int(row[1])

    publication_counter = 0
    node_list = [x.index for x in graph.vs]

    with open(new_data / 'node_list.txt', 'w') as file:
        file.write(str(node_list))

    with open(new_data / 'mapping.txt', 'w') as file:
        file.write(str(mapping))

    with log.scope.info('Delete graph...'):
        del graph

    with log.scope.info('Collecting statistics...'):

        publications = list(publications_in('COMP', between=(1990, 2018)))
        log.info(f'{blue | len(publications)} publications.')

        stats = []
        for publication in publications:

            publication_counter += 1

            authors = []
            for author in publication['authors']:
                authors.append(author['id'])

            # statistics = {}
            statistics = {'publication_id': publication['id']}

            all = True
            for id in authors:
                # log.info(f'id {id}, mapping[id] {mapping[id]}')
                if id not in mapping.keys():
                    all = False
                elif mapping[id] not in node_list:
                    all = False

            if all:
                for author in authors:
                    if str(mapping[author]) in communities.keys():

                        community = f'community {communities[str(mapping[author])]}'

                        if community in statistics.keys():
                            statistics[community] += 1
                        else:
                            statistics[community] = 1

            if publication_counter % 500 == 0:
                log.info(f'{blue | publication_counter} ...')

            stats.append(statistics)

    with log.scope.info('Saving statistics into a file...'):
        with open(new_data / 'stats_largest_cluster.json', 'w') as file:
            json.dump(stats, file)

create_data()