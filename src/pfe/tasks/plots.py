import json
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt

from pfe.misc.log import Pretty
from pfe.misc.log.misc import percents
from pfe.misc.style import blue, bold, gray

if __name__ == '__main__':
    log = Pretty()
    log.info('Starting.')

    data = Path('../../../data/graph/ig')

    with log.scope.info('Reading communities.'):
        with open(data / 'leiden_communities.json', 'r') as file:
            communities = json.load(file)
            communities = [(x, len(y)) for x, y in communities.items()]
            communities.sort(key=lambda x: x[1], reverse=True)  # Sort by community sizes.

    sizes = Counter(y for _, y in communities)
    total = sum(y for _, y in communities)

    log.info(f'The number of authors:       {blue | total}')
    log.info(f'The number of unique sizes:  {blue | len(sizes)}')
    log.info(f'The largest community size:  {blue | max(sizes)}')
    log.info(f'The smallest community size: {blue | min(sizes)}')

    largest = 20

    with log.scope.info(f'The sizes of top {bold | largest} largest communities:'):
        for community, size in communities[:largest]:
            log.info(f'"{community}":'.ljust(7) +
                     f'{blue | str(size).rjust(7)}  {gray | "~"}'
                     f'{percents(size, total, precision=6)}')

    with log.scope.info('Plotting.'):
        _, ax = plt.subplots()

        ax.pie([x*y for x, y in sizes.items()], autopct='%1.01f%%', startangle=90)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        plt.show()
