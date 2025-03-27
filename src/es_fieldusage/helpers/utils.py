"""Utility helper functions"""

import typing as t
from collections import defaultdict
from functools import reduce
from itertools import chain
from operator import getitem, itemgetter
import click
from es_fieldusage.exceptions import ConfigurationException


def convert_mapping(
    data: t.Dict[str, t.Any], new_dict: t.Optional[t.Dict[str, t.Any]] = None
) -> t.Dict[str, t.Any]:
    """
    Convert an Elasticsearch mapping into a dictionary more closely approximating
    the one coming from the field usage API.

    Receive the mapping dict as ``data``
    Strip out "properties" keys. They are not in the field_usage stats paths.
    Set the value at the end of each dict path to 0 (we merge counts from field
    usage later)
    """
    if new_dict is None:
        new_dict = {}
    retval = {}
    for key, value in data.items():
        new_dict[key] = value
        if isinstance(value, dict):
            if 'properties' in value:
                new_dict[key] = value['properties']
                retval[key] = convert_mapping(new_dict[key], new_dict={})
            else:
                retval[key] = 0
    return retval


def detuple(path: t.List[t.Any]) -> t.List[t.Any]:
    """If we used a tuple to access a dict path, we fix it to be a list again here"""
    if len(path) == 1 and isinstance(path[0], tuple):
        return list(path[0])
    return path


def get_value_from_path(data: t.Dict[str, t.Any], path: t.List[t.Any]) -> t.Any:
    """
    Return value from dict ``data``. Recreate all keys from list ``path``
    """
    return reduce(getitem, path, data)


def iterate_paths(
    data: t.Dict[str, t.Any], path: t.Optional[t.List[str]] = None
) -> t.Generator[t.List[str], None, None]:
    """Recursively extract all paths from a dictionary"""
    if path is None:
        path = []
    for key, value in data.items():
        newpath = path + [key]
        if isinstance(value, dict):
            for subkey in iterate_paths(value, newpath):
                yield subkey
        else:
            yield newpath


def output_report(search_pattern: str, report: t.Dict[str, t.Any]) -> None:
    """Output summary report data to command-line/console"""
    # Title
    click.secho('\nSummary Report', overline=True, underline=True, bold=True)
    click.secho('\nSearch Pattern: ', nl=False)
    # Search Pattern
    click.secho(search_pattern, bold=True)
    # Indices Found
    if not isinstance(report['indices'], list):
        click.secho('Index Found: ', nl=False)
        click.secho(f'{report["indices"]}', bold=True)
    else:
        click.secho(f'{len(report["indices"])} ', bold=True, nl=False)
        click.secho('Indices Found: ', nl=False)
        if len(report['indices']) > 3:
            click.secho('(data too big)', bold=True)
        else:
            click.secho(f'{report["indices"]}', bold=True)
    # Total Fields
    click.secho('Total Fields Found: ', nl=False)
    click.secho(report['field_count'], bold=True)
    # Accessed Fields
    click.secho('Accessed Fields: ', nl=False)
    click.secho(len(report['accessed'].keys()), bold=True)
    # Unaccessed Fields
    click.secho('Unaccessed Fields: ', nl=False)
    click.secho(len(report['unaccessed'].keys()), bold=True)


def override_settings(
    data: t.Dict[str, t.Any], new_data: t.Dict[str, t.Any]
) -> t.Dict[str, t.Any]:
    """Override keys in data with values matching in new_data"""
    if not isinstance(new_data, dict):
        raise ConfigurationException('new_data must be of type dict')
    for key in list(new_data.keys()):
        if key in data:
            data[key] = new_data[key]
    return data


def passthrough(func: t.Callable) -> t.Callable:
    """Wrapper to make it easy to store click configuration elsewhere"""
    return lambda a, k: func(*a, **k)


def sort_by_name(data: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
    """Sort dictionary by key alphabetically"""
    return dict(sorted(data.items(), key=itemgetter(0)))


def sort_by_value(data: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
    """Sort dictionary by root key value, descending"""
    return dict(sorted(data.items(), key=itemgetter(1), reverse=True))


def sum_dict_values(data: t.Dict[str, t.Dict[str, t.Any]]) -> t.Dict[str, int]:
    """Sum the values of data dict(s) into a new defaultdict"""
    # Sets up result to have every dictionary key be an integer by default
    result = defaultdict(int)
    dlist = []
    for _, value in data.items():
        dlist.append(value)
    for key, value in chain.from_iterable(d.items() for d in dlist):
        result[key] += int(value)
    return sort_by_name(dict(result))
