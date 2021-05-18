import csv
import json
from operator import itemgetter
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd
import numpy as np
import re



with open("C:/Users/2shel/Desktop/Labex.json", 'r', encoding='UTF-8') as file:
    some = json.load(file)
#
algorithms = ['leiden']

labex = []
labex_groups = []

for algorithm in algorithms:

    with open("C:/Users/2shel/Desktop/Labex.json", 'r', encoding='UTF-8') as file:
        labex_publications = json.load(file)

    for lp in labex_publications:
        labex += list(lp['ids'].values())
    for lp in labex_publications:
        labex_groups.append(set(lp['ids'].values()))

    labex = set(labex)
    print(labex_groups)

    exit()
    for year in range(2013, 2018):
        graph = nx.read_graphml(Path(f'test-data/COMP-data/graph/nice/by_year/int/nx_comp_nice_{year}_int_graph/'
                                     f'{algorithm}_communities_network_{year}.xml'))

        for u in graph.nodes():
            if int(graph.nodes[u]['name_in_18']) in labex:
                graph.nodes[u]['labex'] = 1
            else:
                graph.nodes[u]['labex'] = 0

        # for group in labex_groups:
        #     if len(group) > 1:
        #         for a in group:
        #             for b in group:
        #                 a = int(a)
        #                 b = int(b)
        #
        #                 if graph.has_edge(u, v):
        #                     graph.edges[u, v]['labex'] = 1
        #                 else:
        #                     graph.edges[u, v]['labex'] = 0


        nx.write_graphml(graph, Path(f'test-data/COMP-data/graph/nice/by_year/int/nx_comp_nice_{year}_int_graph/'
                                     f'{algorithm}_communities_network_{year}.xml'))

    for year in range(2018, 2019):
        graph = nx.read_graphml(Path(f'test-data/COMP-data/graph/nice/by_year/int/nx_comp_nice_{year}_int_graph/'
                                     f'{algorithm}_communities_network.xml'))

        for u in graph.nodes():
            if int(u) in labex:
                graph.nodes[u]['labex'] = 1
            else:
                graph.nodes[u]['labex'] = 0

        nx.write_graphml(graph, Path(f'test-data/COMP-data/graph/nice/by_year/int/nx_comp_nice_{year}_int_graph/'
                                     f'{algorithm}_communities_network_{year}.xml'))