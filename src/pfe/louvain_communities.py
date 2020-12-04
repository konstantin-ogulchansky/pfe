import json


def save_communities(partition, file):
    # save communities into file
    components = {}
    for n in partition:
        if partition[n] in components:
            components[partition[n]] += 1
        else:
            components[partition[n]] = 1

    with(open(f'{file}.json', 'w')) as components_file:
        json.dump(components, components_file)


with(open('components.json', 'r')) as components_file:
    components = dict(json.load(components_file))


def small_groups(up_to):
    # group communities of 2..'n' members
    small_groups = set()
    groupped = dict()
    for key in components.keys():
        for members in range(2, up_to + 1):
            if components[key] == members:

                if f'{members}-com' in groupped:
                    groupped[f'{members}-com'] += 1
                    small_groups.add(key)

                else:
                    groupped[f'{members}-com'] = 1
                    small_groups.add(key)

    return small_groups, groupped


if __name__ == '__main__':

    from pfe.misc.log import timestamped
    import community as louvain
    import networkx as nx

    timestamped('Start: nx_graph')
    nx_graph = nx.read_weighted_edgelist('nx_full_graph')
    timestamped('Finish')

    print('Computing Louvain partitions')

    # detect commuities
    timestamped('Started')
    partition = louvain.best_partition(nx_graph)
    timestamped('Finished')


    save_communities(partition, 'components_nx_full_graph')
# for group, _ in small_groups(up_to=10):
#     del components[group]
