from pathlib import Path
from typing import Tuple, Any, Iterable

from pfe.preprocessing.clean import load, save


def publications_in(*domains: str,
                    between: Tuple[int, int],
                    **kwargs: Any) -> Iterable[dict]:

    def appropriate(publication: dict) -> bool:
        if len(publication['authors']) >= 100:
            return False

        for author in publication['authors']:
            if author['affiliation_city'] in ['Nice', 'Sophia Antipolis']:
                return True

        return False

    directory = Path('../../..')
    new_directory = Path('test-data/COMP(Nice)')

    # Find the root of the repository.
    while all(x.name != '.gitignore' for x in directory.iterdir()):
        directory = directory.parent

    files = [directory / 'data' / 'clean' / domain / f'{domain}-{year}.json'
             for domain in domains
             for year in range(between[0], between[1] + 1)]

    for file in files:
        publications = load(from_=file)

        to_save = []
        for publication in publications:
            if appropriate(publication):
                to_save.append(publication)

        save(to_save, to=new_directory/file.name)


if __name__ == '__main__':
    from pfe.misc.log import Pretty

    log = Pretty()
    log.info('Starting.')

    with log.scope.info(f'Saving'):
        nice = publications_in('COMP', between=(1990, 2018), log=log)

