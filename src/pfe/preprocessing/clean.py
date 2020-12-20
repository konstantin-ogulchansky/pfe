"""
Contains functions for cleaning the extracted publication data.
"""

import json
from typing import Any, Union
from pathlib import Path

from pfe.misc.log import Pretty, Log, Nothing
from pfe.misc.style import magenta, blue, gray


def clean(data: dict[str, Any], log: Log = Nothing()) -> list[dict[str, Any]]:
    """Cleans the provided `data` by removing unused fields.

    :param data: a dictionary that represents a JSON file
                 with collaboration data.
    :param log: an instance of `Log` to log the execution with.

    :returns: a list that contains cleaned
              information about publications.
    """

    def affiliations(publication, id, field):
        if isinstance(id, list):
            return [affiliations(publication, x, field) for x in id]

        if isinstance(publication['affiliation'], list):
            for affiliation in publication['affiliation']:
                if affiliation['afid'] == id:
                    return affiliation[field]
        else:
            return publication['affiliation'][field]

    def city(publication, id):
        return affiliations(publication, id, 'affiliation-city')

    def country(publication, id):
        return affiliations(publication, id, 'affiliation-country')

    def authors(publication):
        return author if isinstance(author := publication['author'], list) else [author]

    result = []

    for publication in data['search-results']['entry']:
        try:
            result.append({
                'id': publication.get('dc:identifier'),
                'date': publication.get('prism:coverDate'),
                'authors': [{
                    'id': author.get('authid'),
                    'name': author.get('authname'),
                    'affiliation_id': (id := author.get('afid')),
                    'affiliation_city': city(publication, id),
                    'affiliation_country': country(publication, id)
                } for author in authors(publication)]
            })
        except KeyError as error:
            log.warn(f'Key {magenta | str(error)} not found in \n'
                     f'{gray | "|"} {publication}')

    return result


def load(*, from_: Union[str, Path]) -> dict[str, Any]:
    """Loads JSON data from a file.

    :param from_: a path to a file to load data from.

    :returns: loaded JSON data.
    """

    with open(from_, 'r') as file:
        return json.load(file)


def save(data: list[dict[str, Any]], *, to: Union[str, Path]):
    """Saves the provided JSON data to a file.

    :param data: JSON data to save.
    :param to: a path to a file to save data to.
    """

    with open(to, 'w') as file:
        json.dump(data, file)


if __name__ == '__main__':
    log = Pretty()
    log.info('Starting.')

    # We assume that data is stored in a directory
    # with the following structure.
    #
    #     data/
    #     |- comp/
    #        |- 2019.json
    #        |- 2020.json
    #     |- math/
    #        |- 2020.json
    #        ...
    #
    # Names of directories and files may differ.
    # Cleaned data will be stored in a directory
    # with equivalent structure.

    old_directory = Path('../../../data/raw')
    new_directory = Path('../../../data/clean')

    # Create new folder for cleaned data.
    if new_directory.exists():
        raise ValueError(f'Cannot clean data: "{new_directory}" already exists.')

    new_directory.mkdir()

    for old_subdirectory in old_directory.iterdir():
        new_subdirectory = new_directory / old_subdirectory.name
        new_subdirectory.mkdir()

        for old_file in old_subdirectory.iterdir():
            if old_file.suffix != '.json':
                continue

            new_file = new_subdirectory / old_file.name

            with log.scope.info(f'Cleaning "{magenta | old_file}".'):
                data = load(from_=old_file)
                save(clean(data, log=log), to=new_file)

                log.info(f'Old file size: {blue | old_file.stat().st_size / (1024 * 1024)} Mb.')
                log.info(f'New file size: {blue | new_file.stat().st_size / (1024 * 1024)} Mb.')

    log.info('Finished.')
