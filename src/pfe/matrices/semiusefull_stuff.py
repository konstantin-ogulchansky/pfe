import json
from pathlib import Path

from pfe.misc.log import Pretty, Log
from pfe.misc.style import blue


def show_number_of_publications_among_1_2_3and_more_communities():
    log: Log = Pretty()
    log.info('Starting...')

    data = Path('../../../data/graph/ig')
    test_stuff = Path('test-data')

    with log.scope.info('Reading authors-communities...'):
        with open(test_stuff / 'stats_largest_cluster.json', 'r') as file:
            stats = json.load(file)

    n = 0
    one_comm = 0
    two_comm = 0
    all_other_comm = 0
    z = 0
    with log.scope.info('Counting publications by number of communities...'):
        for s in stats:
            s.pop('publication_id')
            if len(s) == 1:
                one_comm += 1
            elif len(s) == 2:
                two_comm += 1
            elif len(s) >= 3:
                all_other_comm += 1
            elif len(s) < 1:
                z += 1
            n += 1

    log.info(f'Publications in: ')
    log.info(f'1 community: {blue | one_comm} ')
    log.info(f'2 communities: {blue | two_comm} ')
    log.info(f'all other: {blue | all_other_comm} ')
    log.info(f'Total: {blue | n} ')

    print(z)
    print(n - z)
    print(one_comm + two_comm + all_other_comm)
    print()
    print(one_comm / (n - z))
    print(two_comm / (n - z))
    print(all_other_comm / (n - z))