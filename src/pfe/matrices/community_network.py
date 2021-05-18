import json
import os
import networkx as nx

from os.path import basename
from pathlib import Path

from pfe.misc.log import Pretty
from pfe.misc.style import blue

log = Pretty()


root_path = Path('test-data/COMP-data/graph/nice')
folders = [
    # all_years_f := root_path/Path('all_years/float'),
    # all_years_i := root_path/Path('all_years/int'),
    by_year_i := root_path/Path('by_year/int'),
    # by_year_f := root_path / Path('by_year/float'),
    # by_year_fs := root_path/Path('by_year/float_selfloop'),
]
algorithms = ['leiden', 'louvain']

# todo: mark labex communities

for algorithm in algorithms:
    # for graph_folder in folders:
    #     for subfolder in graph_folder.iterdir():
    #         graph = nx.Graph()
    #         if os.path.isdir(subfolder):
    for year in range(2013, 2018):
        graph = nx.Graph()

        subfolder = Path(f'test-data/COMP-data/graph/nice/by_year/int/nx_comp_nice_{year}_int_graph')
        with open(subfolder/ f'{algorithm}_stability_thing.json', 'r') as file:
            matching = json.load(file)
            matching.pop(0)

        with open(subfolder / f'stats_largest_cluster_{algorithm}.json', 'r') as file:
            stats = json.load(file)

        for s in stats:
            s.pop('publication_id')

            nodes = []
            if len(s) >= 1:
                for i, k in zip(range(len(s)), s.keys()):
                    nodes.append(int(k.split()[1]))
                nodes.sort()

            print(nodes)

            for node in nodes:
                if node not in graph.nodes():
                    graph.add_node(node)

            for u in nodes:
                for v in nodes:
                    if u != v and not graph.has_edge(u, v):
                        graph.add_edge(u, v, weight=1)

                    if graph.has_edge(u, v):
                        graph.edges[u, v]['weight'] += 1

        for community_year in matching:
            print(community_year)
            # graph.nodes[community_year['from_community']]['name_in_18'] = \
            graph.nodes[int(community_year['from_community'])]['name_in_18'] = \
                community_year['in_community']

        # with open("C:/Users/2shel/Desktop/Labex.json", 'r', encoding='UTF-8') as file:
        #     labex_publications = json.load(file)




        # log.info(f'{algorithm} Plotting.. {blue| basename(subfolder)}')
        # plt.clf()
        # nx.draw(graph)
        # # nx.draw_networkx_labels(graph)
        # plt.savefig(subfolder/f'{algorithm}_communities_network.png')

        nx.write_graphml(graph, subfolder/f'{algorithm}_communities_network_{year}.xml')