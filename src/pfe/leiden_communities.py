# *Vertices 2232963
# *Edges
import json
import igraph as ig
from pfe.misc.log import timestamped


timestamped('Start: ig_graph')
graph = ig.Graph.Read_Pajek('ig-graph-data/ig_full_graph_relabeled_nodes.net')
timestamped('Finish')


timestamped('Leiden: computing communities')
partitions = graph.community_leiden(objective_function="modularity", weights='weight')

communities_file = 'leiden_comp_communities'
timestamped('Leiden: saving communities into file')
with(open(f'{communities_file}.json', 'w')) as components_file:
    json.dump(dict(enumerate(x for x in partitions)), components_file)

print()
print(partitions.modularity)
print()
timestamped('Leiden: saving modularity value into file')
modularity_file = 'leiden_modularity'
with(open(f'{modularity_file}.json', 'w')) as components_file:
    json.dump(partitions.modularity, components_file)


