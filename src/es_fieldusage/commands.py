"""Sub-commands for Click CLI"""
import os
import logging
import click
from es_client.helpers import utils as escl
from es_fieldusage.defaults import FILEPATH_OVERRIDE, EPILOG, get_context_settings
from es_fieldusage.exceptions import FatalException
from es_fieldusage.helpers.client import get_args, get_client
from es_fieldusage.helpers.utils import cli_opts, is_docker, output_report
from es_fieldusage.main import FieldUsage

LOGGER = logging.getLogger(__name__)

ONOFF = {'on': 'show-', 'off': 'hide-'}
click_opt_wrap = escl.option_wrapper()

def get_per_index(field_usage, per_index):
    """Return the per_index data set for reporting"""
    if per_index:
        try:
            all_data = field_usage.per_index_report
        except Exception as exc:
            LOGGER.critical('Unable to get per_index_report data: %s', exc)
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
        # In order to write newlines to a file descriptor, they must be part of the line
        yield f'{line}\n'

def override_filepath():
    """Override the default filepath if we're running Docker"""
    if is_docker():
        return {'default': FILEPATH_OVERRIDE}
    return {}

@click.command(context_settings=get_context_settings(), epilog=EPILOG)
@click_opt_wrap(*cli_opts('report', onoff=ONOFF))
@click_opt_wrap(*cli_opts('headers', onoff=ONOFF))
@click_opt_wrap(*cli_opts('accessed', onoff=ONOFF))
@click_opt_wrap(*cli_opts('unaccessed', onoff=ONOFF))
@click_opt_wrap(*cli_opts('counts', onoff=ONOFF))
@click_opt_wrap(*cli_opts('delimiter'))
@click.argument('search_pattern', type=str, nargs=1)
@click.pass_context
def stdout(
    ctx, show_report, show_headers, show_accessed, show_unaccessed, show_counts, delimiter,
    search_pattern):
    """
    Display field usage information on the console for SEARCH_PATTERN

    $ es-fieldusage stdout [OPTIONS] SEARCH_PATTERN

    This is powerful if you want to pipe the output through grep for only certain fields or
    patterns:

    $ es-fieldusage stdout --hide-report --hide-headers --show-unaccessed 'index-*' | grep process
    """
    client_args, other_args = get_args(ctx.parent.params)
    try:
        field_usage = FieldUsage(client_args, other_args, search_pattern)
    except Exception as exc:
        LOGGER.critical('Exception encountered: %s', exc)
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

@click.command(context_settings=get_context_settings(), epilog=EPILOG)
@click_opt_wrap(*cli_opts('report', onoff=ONOFF))
@click_opt_wrap(*cli_opts('accessed', onoff=ONOFF, override={'default': True}))
@click_opt_wrap(*cli_opts('unaccessed', onoff=ONOFF, override={'default': True}))
@click_opt_wrap(*cli_opts('counts', onoff=ONOFF, override={'default': True}))
@click_opt_wrap(*cli_opts('index', {'on': 'per-', 'off': 'not-per-'}))
@click_opt_wrap(*cli_opts('filepath', override=override_filepath()))
@click_opt_wrap(*cli_opts('prefix'))
@click_opt_wrap(*cli_opts('suffix'))
@click_opt_wrap(*cli_opts('delimiter'))
@click.argument('search_pattern', type=str, nargs=1)
@click.pass_context
def file(
    ctx, show_report, show_accessed, show_unaccessed, show_counts, per_index, filepath, prefix,
    suffix, delimiter, search_pattern):
    """
    Write field usage information to file for SEARCH_PATTERN

    $ es_fieldusage file [OPTIONS] SEARCH_PATTERN

    When writing to file, the filename will be {prefix}-{INDEXNAME}.{suffix} where INDEXNAME will
    be the name of the index if the --per-index option is used, or 'all_indices' if not.

    This allows you to write to one file per index automatically, should that be your desire.
    """
    client_args, other_args = get_args(ctx.parent.params)
    try:
        field_usage = FieldUsage(client_args, other_args, search_pattern)
    except Exception as exc:
        LOGGER.critical('Exception encountered: %s', exc)
        raise FatalException from exc
    if show_report:
        output_report(search_pattern, field_usage.report)
        click.secho()

    all_data = get_per_index(field_usage, per_index)

    files_written = []
    for idx in list(all_data.keys()):
        fname = f'{prefix}-{idx}.{suffix}'
        filename = os.path.join(filepath, fname)
        files_written.append(fname)
        for key, boolval in {'accessed': show_accessed, 'unaccessed': show_unaccessed}.items():
            if boolval:
                generator = output_generator(all_data[idx][key], show_counts, delimiter)
                with open(filename, 'w', encoding='utf-8') as fdesc:
                    fdesc.writelines(generator)
    click.secho('Number of files written: ', nl=False)
    click.secho(len(files_written), bold=True)
    click.secho('Filenames: ', nl=False)
    if len(files_written) > 3:
        click.secho(files_written[0:3], bold=True, nl=False)
        click.secho(' ... (too many to show)')
    else:
        click.secho(files_written, bold=True)

@click.command(context_settings=get_context_settings(), epilog=EPILOG)
@click.argument('search_pattern', type=str, nargs=1)
@click.pass_context
def show_indices(ctx, search_pattern):
    """
    Show indices on the console matching SEARCH_PATTERN

    $ es-fieldusage show_indices SEARCH_PATTERN

    This is included as a way to ensure you are seeing the indices you expect before using the file
    or stdout commands.
    """
    client_args, other_args = get_args(ctx.parent.params)
    try:
        client = get_client(configdict={
            'elasticsearch': {
                'client': escl.prune_nones(client_args.asdict()),
                'other_settings': escl.prune_nones(other_args.asdict())
            }
        })
    except Exception as exc:
        LOGGER.critical('Exception encountered: %s', exc)
        raise FatalException from exc
    cat = client.cat.indices(index=search_pattern, h='index', format='json')
    indices = []
    for item in cat:
        indices.append(item['index'])
    indices.sort()
    # Output
    ## Search Pattern
    click.secho('\nSearch Pattern', nl=False, overline=True, underline=True, bold=True)
    click.secho(f': {search_pattern}', bold=True)
    ## Indices Found
    if len(indices) == 1:
        click.secho('\nIndex Found', nl=False, overline=True, underline=True, bold=True)
        click.secho(f': {indices[0]}', bold=True)
    else:
        click.secho(f'\n{len(indices)} ', overline=True, underline=True, bold=True, nl=False)
        click.secho('Indices Found', overline=True, underline=True, bold=True, nl=False)
        click.secho(': ')
        for idx in indices:
            click.secho(idx)
