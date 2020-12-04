import csv
from pathlib import Path

import networkx as nx
import igraph as ig

from pfe.misc.log import timestamped
from pfe.parse import parse, publications_in

# graph = nx.Graph()
#
# directory = Path('../../data/clean')
# for subdirectory in directory.iterdir():
#     timestamped(f'Start {subdirectory.name}')
#     graph = parse(publications_in(subdirectory.name, between=(1990, 2018), log=timestamped), into=graph)
#     timestamped('Finish')

timestamped('Start')
nx_graph = nx.read_weighted_edgelist('nx_full_graph')
timestamped('Finish')

timestamped('Start: rename nodes')

mapping = dict(zip(nx_graph, range(0, len(nx_graph.nodes()))))
nx_graph = nx.relabel_nodes(nx_graph, mapping, copy=False)

timestamped('Start: save mapping')

w = csv.writer(open("mapping.csv", "w"))
for key, val in mapping.items():
    w.writerow([key, val])

timestamped('Start: save to file')
nx.write_weighted_edgelist(nx_graph, 'nx_full_graph_relabeled_nodes')



