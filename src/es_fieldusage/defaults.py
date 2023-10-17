"""Default values and constants"""
import os
from shutil import get_terminal_size
import click
from six import string_types
from voluptuous import All, Any, Coerce, Optional, Schema

# pylint: disable=E1120

# This value is hard-coded in the Dockerfile, so don't change it

FILEPATH_OVERRIDE = '/fileoutput'

EPILOG = 'Learn more at https://github.com/untergeek/es-fieldusage'

HELP_OPTIONS = {'help_option_names': ['-h', '--help']}

CLI_OPTIONS = {
    'loglevel': {
        'help': 'Log level',
        "type": click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
    },
    'logfile': {'help': 'Log file', 'type': str},
    'logformat': {
        'help': 'Log output format',
        "type": click.Choice(['default', 'ecs'])
    },
    'report':{
        'help': 'Show a summary report',
        'default': True,
        'show_default': True,
    },
    'headers':{
        'help': 'Show block headers for un|accessed fields',
        'default': True,
        'show_default': True,
    },
    'accessed':{
        'help': 'Show accessed fields',
        'default': False,
        'show_default': True,
    },
    'unaccessed':{
        'help': 'Show unaccessed fields',
        'default': False,
        'show_default': True,
    },
    'counts':{
        'help': 'Show field access counts',
        'default': False,
        'show_default': True,
    },
    'delimiter':{
        'help': 'Value delimiter if access counts are shown',
        'type': str,
        'default': ',',
        'show_default': True,
    },
    'index':{
        'help': 'Create one file per index found',
        'default': False,
        'show_default': True,
    },
    'filepath':{
        'help': 'Path where files will be written',
        'default': os.getcwd(),
        'show_default': True,
    },
    'prefix':{
        'help': 'Filename prefix',
        'default': 'es_fieldusage',
        'show_default': True,
    },
    'suffix':{
        'help': 'Filename suffix',
        'default': 'csv',
        'show_default': True,
    },
    'show_hidden': {'help': 'Show all options', 'is_flag': True, 'default': False}
}

def click_options():
    """Return the max version"""
    return CLI_OPTIONS

# Configuration file: logging
def config_logging():
    """
    Logging schema with defaults:

    .. code-block:: yaml

        logging:
          loglevel: INFO
          logfile: None
          logformat: default
          blacklist: ['elastic_transport', 'urllib3']

    :returns: A valid :py:class:`~.voluptuous.schema_builder.Schema` of all acceptable values with
        the default values set.
    :rtype: :py:class:`~.voluptuous.schema_builder.Schema`
    """
    return Schema(
        {
            Optional('loglevel', default='INFO'):
                Any(None, 'NOTSET', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL',
                    All(Coerce(int), Any(0, 10, 20, 30, 40, 50))
                    ),
            Optional('logfile', default=None): Any(None, *string_types),
            Optional('logformat', default='default'):
                Any(None, All(Any(*string_types), Any('default', 'ecs'))),
            Optional('blacklist', default=['elastic_transport', 'urllib3']): Any(None, list),
        }
    )

def get_context_settings():
    """Return Click context settings dictionary"""
    return {**get_width(), **HELP_OPTIONS}

def get_width():
    """Determine terminal width"""
    return {"max_content_width": get_terminal_size()[0]}
