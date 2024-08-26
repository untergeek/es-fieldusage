"""Sub-commands for Click CLI"""

import os
from datetime import datetime, timezone
import json
import logging
import click
from es_client.helpers import config as escl
from es_client.helpers.logging import is_docker
from es_client.helpers.utils import option_wrapper
from es_fieldusage.defaults import OPTS, FILEPATH_OVERRIDE, EPILOG
from es_fieldusage.exceptions import FatalException
from es_fieldusage.helpers.utils import output_report
from es_fieldusage.main import FieldUsage

SHW = {'on': 'show-', 'off': 'hide-'}
TRU = {'default': True}
WRP = option_wrapper()

# pylint: disable=R0913,R0914


def get_per_index(field_usage, per_index):
    """Return the per_index data set for reporting"""
    logger = logging.getLogger(__name__)
    if per_index:
        try:
            all_data = field_usage.per_index_report
        except Exception as exc:
            logger.critical('Unable to get per_index_report data: %s', exc)
            raise FatalException from exc
    else:
        all_data = {
            'all_indices': {
                'accessed': field_usage.report['accessed'],
                'unaccessed': field_usage.report['unaccessed'],
            }
        }
    return all_data


def format_delimiter(value):
    """Return a formatted delimiter"""
    delimiter = ''
    if value == ':':
        delimiter = f'{value} '
    elif value == '=':
        delimiter = f' {value} '
    else:
        delimiter = value
    return delimiter


def header_msg(msg, show):
    """Return the message to show if show is True"""
    if not show:
        msg = ''
    return msg


def printout(data, show_counts, raw_delimiter):
    """Print output to stdout based on the provided values"""
    for line in output_generator(data, show_counts, raw_delimiter):
        # Since the generator is adding newlines, we set nl=False here
        click.secho(line, nl=False)


def output_generator(data, show_counts, raw_delimiter):
    """Generate output iterator based on the provided values"""
    delimiter = format_delimiter(raw_delimiter)
    for key, value in data.items():
        line = ''
        if show_counts:
            line = f'{key}{delimiter}{value}'
        else:
            line = f'{key}'
        # In order to write newlines to a file descriptor, they must be part of
        # the line
        yield f'{line}\n'


def override_filepath():
    """Override the default filepath if we're running Docker"""
    if is_docker():
        return {'default': FILEPATH_OVERRIDE}
    return {}


@click.command(epilog=EPILOG)
@WRP(*escl.cli_opts('report', settings=OPTS, onoff=SHW))
@WRP(*escl.cli_opts('headers', settings=OPTS, onoff=SHW))
@WRP(*escl.cli_opts('accessed', settings=OPTS, onoff=SHW))
@WRP(*escl.cli_opts('unaccessed', settings=OPTS, onoff=SHW))
@WRP(*escl.cli_opts('counts', settings=OPTS, onoff=SHW))
@WRP(*escl.cli_opts('delimiter', settings=OPTS))
@click.argument('search_pattern', type=str, nargs=1)
@click.pass_context
def stdout(
    ctx,
    show_report,
    show_headers,
    show_accessed,
    show_unaccessed,
    show_counts,
    delimiter,
    search_pattern,
):
    """
    Display field usage information on the console for SEARCH_PATTERN

    $ es-fieldusage stdout [OPTIONS] SEARCH_PATTERN

    This is powerful if you want to pipe the output through grep for only certain
    fields or patterns:

    $ es-fieldusage stdout --hide-report --hide-headers --show-unaccessed 'index-*' \
     | grep process
    """
    logger = logging.getLogger(__name__)
    try:
        field_usage = FieldUsage(ctx.obj['configdict'], search_pattern)
    except Exception as exc:
        logger.critical('Exception encountered: %s', exc)
        raise FatalException from exc
    if show_report:
        output_report(search_pattern, field_usage.report)
    if show_accessed:
        msg = header_msg('\nAccessed Fields (in descending frequency):', show_headers)
        click.secho(msg, overline=show_headers, underline=show_headers, bold=True)
        printout(field_usage.report['accessed'], show_counts, delimiter)
    if show_unaccessed:
        msg = header_msg('\nUnaccessed Fields', show_headers)
        click.secho(msg, overline=show_headers, underline=show_headers, bold=True)
        printout(field_usage.report['unaccessed'], show_counts, delimiter)


@click.command(epilog=EPILOG)
@WRP(*escl.cli_opts('report', settings=OPTS, onoff=SHW))
@WRP(*escl.cli_opts('accessed', settings=OPTS, onoff=SHW, override=TRU))
@WRP(*escl.cli_opts('unaccessed', settings=OPTS, onoff=SHW, override=TRU))
@WRP(*escl.cli_opts('counts', settings=OPTS, onoff=SHW, override=TRU))
@WRP(*escl.cli_opts('index', settings=OPTS, onoff={'on': 'per-', 'off': 'not-per-'}))
@WRP(*escl.cli_opts('filepath', settings=OPTS, override=override_filepath()))
@WRP(*escl.cli_opts('prefix', settings=OPTS))
@WRP(*escl.cli_opts('suffix', settings=OPTS))
@WRP(*escl.cli_opts('delimiter', settings=OPTS))
@click.argument('search_pattern', type=str, nargs=1)
@click.pass_context
def file(
    ctx,
    show_report,
    show_accessed,
    show_unaccessed,
    show_counts,
    per_index,
    filepath,
    prefix,
    suffix,
    delimiter,
    search_pattern,
):
    """
    Write field usage information to file for SEARCH_PATTERN

    $ es_fieldusage file [OPTIONS] SEARCH_PATTERN

    When writing to file, the filename will be {prefix}-{INDEXNAME}.{suffix}
    where INDEXNAME will be the name of the index if the --per-index option is
    used, or 'all_indices' if not.

    This allows you to write to one file per index automatically, should that
    be your desire.
    """
    logger = logging.getLogger(__name__)
    try:
        field_usage = FieldUsage(ctx.obj['configdict'], search_pattern)
    except Exception as exc:
        logger.critical('Exception encountered: %s', exc)
        raise FatalException from exc
    if show_report:
        output_report(search_pattern, field_usage.report)
        click.secho()

    all_data = get_per_index(field_usage, per_index)

    files_written = []
    for idx in list(all_data.keys()):
        fname = f'{prefix}-{idx}.{suffix}'
        filename = os.path.join(filepath, fname)

        # if the file already exists, remove it first so we don't append to old
        # data below
        if os.path.exists(filename):
            os.remove(filename)

        # JSON output can be done from a dictionary. In order to preserve the
        # ability to show/hide accessed & unaccessed, I need a clean dictionary
        output = {}
        files_written.append(fname)
        for key, boolval in {
            'accessed': show_accessed,
            'unaccessed': show_unaccessed,
        }.items():
            if boolval:
                output.update(all_data[idx][key])
                if not suffix == 'json':
                    generator = output_generator(
                        all_data[idx][key], show_counts, delimiter
                    )
                    with open(filename, 'a', encoding='utf-8') as fdesc:
                        fdesc.writelines(generator)
        # Now we write output as a JSON object, if we selected that
        if suffix == 'json':
            with open(filename, 'a', encoding='utf-8') as fdesc:
                json.dump(output, fdesc, indent=2)
                fdesc.write('\n')
    click.secho('Number of files written: ', nl=False)
    click.secho(len(files_written), bold=True)
    click.secho('Filenames: ', nl=False)
    if len(files_written) > 3:
        click.secho(files_written[0:3], bold=True, nl=False)
        click.secho(' ... (too many to show)')
    else:
        click.secho(files_written, bold=True)


@click.command(epilog=EPILOG)
@WRP(*escl.cli_opts('report', settings=OPTS, onoff=SHW))
@WRP(*escl.cli_opts('accessed', settings=OPTS, onoff=SHW, override=TRU))
@WRP(*escl.cli_opts('unaccessed', settings=OPTS, onoff=SHW, override=TRU))
@WRP(*escl.cli_opts('index', settings=OPTS, onoff={'on': 'per-', 'off': 'not-per-'}))
@WRP(*escl.cli_opts('indexname', settings=OPTS))
@click.argument('search_pattern', type=str, nargs=1)
@click.pass_context
def index(
    ctx,
    show_report,
    show_accessed,
    show_unaccessed,
    per_index,
    indexname,
    search_pattern,
):
    """
    Write field usage information to file for SEARCH_PATTERN

    $ es_fieldusage index [OPTIONS] SEARCH_PATTERN

    This will write a document per fieldname per index found in SEARCH_PATTERN
    to INDEXNAME, where the JSON structure is:

    {
      "index": SOURCEINDEXNAME,
      "field": {
        "name": "FIELDNAME",
        "count": COUNT
      }
    }
    """
    logger = logging.getLogger(__name__)
    logger.debug('indexname = %s', indexname)
    timestamp = f"{datetime.now(timezone.utc).isoformat().split('.')[0]}.000Z"
    try:
        field_usage = FieldUsage(ctx.obj['configdict'], search_pattern)
    except Exception as exc:
        logger.critical('Exception encountered: %s', exc)
        raise FatalException from exc
    # client = field_usage.client
    if show_report:
        output_report(search_pattern, field_usage.report)
        click.secho()

    all_data = get_per_index(field_usage, per_index)

    # TESTING
    fname = 'testing'
    filepath = os.getcwd()
    filename = os.path.join(filepath, fname)

    # If the file already exists, remove it so we don't append to old data
    if os.path.exists(filename):
        os.remove(filename)
    # END TESTING

    output = []
    for idx in list(all_data.keys()):
        for key, boolval in {
            'accessed': show_accessed,
            'unaccessed': show_unaccessed,
        }.items():
            if boolval:
                for fieldname, value in all_data[idx][key].items():
                    obj = {
                        '@timestamp': timestamp,
                        'index': idx,
                        'field': {'name': fieldname, 'count': value},
                    }
                    output.append(obj)

    # TESTING
    with open(filename, 'a', encoding='utf-8') as fdesc:
        json.dump(output, fdesc, indent=2)
        fdesc.write('\n')
    # END TESTING


@click.command(epilog=EPILOG)
@click.argument('search_pattern', type=str, nargs=1)
@click.pass_context
def show_indices(ctx, search_pattern):
    """
    Show indices on the console matching SEARCH_PATTERN

    $ es-fieldusage show_indices SEARCH_PATTERN

    This is included as a way to ensure you are seeing the indices you expect
    before using the file or stdout commands.
    """
    logger = logging.getLogger(__name__)
    try:
        client = escl.get_client(configdict=ctx.obj['configdict'])
    except Exception as exc:
        logger.critical('Exception encountered: %s', exc)
        raise FatalException from exc
    cat = client.cat.indices(index=search_pattern, h='index', format='json')
    indices = []
    for item in cat:
        indices.append(item['index'])
    indices.sort()
    # Output
    # Search Pattern
    click.secho('\nSearch Pattern', nl=False, overline=True, underline=True, bold=True)
    click.secho(f': {search_pattern}', bold=True)
    # Indices Found
    if len(indices) == 1:
        click.secho('\nIndex Found', nl=False, overline=True, underline=True, bold=True)
        click.secho(f': {indices[0]}', bold=True)
    else:
        click.secho(
            f'\n{len(indices)} ', overline=True, underline=True, bold=True, nl=False
        )
        click.secho('Indices Found', overline=True, underline=True, bold=True, nl=False)
        click.secho(': ')
        for idx in indices:
            click.secho(idx)
