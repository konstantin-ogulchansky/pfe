import matplotlib.pyplot as plt

from pfe.matrices.matrix import *
from pfe.matrices.plot_heatmap import plot_matrix
from pfe.misc.log import Log, Pretty

log: Log = Pretty()
log.info('Starting...')

data = Path('../../../data/graph/ig')
test_stuff = Path('test-data')


def plot_cumulative_community_sizes(percent):
    community_size = community_sizes()

    y = list(sorted(community_size.values(), reverse=True))
    total = sum(y)
    z = [sum(y[:i + 1]) for i in range(len(y))]

    x = [x / total for x in z]

    def find_index_of(l, val):
        for i in range(len(l)):
            if abs(l[i] - val) <= .003:
                print(i)
                return i

    plt.clf()
    # plt.plot([x / len(y) for x in z],'o')
    fig, ax = plt.subplots(figsize=(10, 6))
    plt.xscale('log')
    ax.plot(x, 'o')
    plt.axhline(y=percent)
    plt.axvline(x=find_index_of(x, percent))

    fig.suptitle('Distribution of community sizes')
    ax.set_title(f'To get {percent * 100}% of the network about {find_index_of(x, percent)} largest communities needed')
    plt.xlabel('number of communities')
    plt.ylabel('part of nodes of the network')

    ax.set_axisbelow(True)
    ax.grid(linestyle='--')
    plt.savefig(test_stuff / f'community_size_{percent}.png')
    plt.show()

    # sns.ecdfplot(community_size)
    # plt.xlabel('community sizes')
    # plt.savefig(test_stuff / f'community_size_cdf.png')
    # plt.show()


def plot_matrix_restricted_by_n_members(n_members):
    odd_communities = get_communities_with_more_than_n_members(n_members)
    n_communities = number_of_communities()

    m = matrix()
    m = pd.DataFrame(m, [str(i) for i in range(n_communities)], [str(i) for i in range(n_communities)])
    m = add_row_with_community_size(m)

    m = exclude_columns(m, odd_communities)
    m = fill_diagonal(m)

    k = prob_matrix(m)

    title = 'Probability matrix'
    subtitle = f'Communities with {n_members} or more'

    if 'sizes' in k.columns.tolist():
        plot_matrix(k, f'matrix_restricted_by_n_members_{n_members}_prob', title, subtitle, prob=True,
                    exclude_columns=True)
    else:
        plot_matrix(k, f'matrix_restricted_by_n_members_{n_members}_prob', title, subtitle, prob=True)


def plot_matrix_restricted_by_n_largest_communities(n_largest):
    largest_communities = get_n_largest_communities(n_largest)
    print(largest_communities)
    print(largest_communities)
    print(largest_communities)
    n_communities = number_of_communities()

    m = matrix()
    m = pd.DataFrame(m, [str(i) for i in range(n_communities)], [str(i) for i in range(n_communities)])
    m = add_row_with_community_size(m)

    m = keep_columns(m, largest_communities)
    m = fill_diagonal(m)

    k = prob_matrix(m)

    title = 'Probability matrix'
    subtitle = f'{n_largest} largest communities'

    if 'sizes' in k.columns.tolist():
        plot_matrix(k, f'matrix_restricted_by_n_largest_communities_{n_largest}_prob', title, subtitle, prob=True,
                    exclude_columns=True)
    else:
        plot_matrix(k, f'matrix_restricted_by_n_largest_communities_{n_largest}_prob', title, subtitle, prob=True)


def get_communities_with_more_than_n_members(n_members):
    c_sizes = community_sizes()
    odd_communities = [i for i in c_sizes.keys() if c_sizes[i] < n_members]

    return odd_communities


def get_n_largest_communities(n):
    community_size = community_sizes()
    y = list(sorted(community_size.values(), reverse=True))
    y = y[:n]

    def get_key(val):
        for key, value in community_size.items():
            if val == value:
                return key

    return [get_key(x) for x in y]


plot_matrix_restricted_by_n_largest_communities(32)
plot_matrix_restricted_by_n_largest_communities(42)
plot_matrix_restricted_by_n_largest_communities(50)

plot_matrix_restricted_by_n_members(1000)
plot_matrix_restricted_by_n_members(1500)
plot_matrix_restricted_by_n_members(4000)
