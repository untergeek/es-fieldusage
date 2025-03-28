"""Default values and constants"""

# pylint: disable=E1120
import typing as t
import os


# This value is hard-coded in the Dockerfile, so don't change it
FILEPATH_OVERRIDE: str = '/fileoutput'

INDEXNAME: str = 'es-fieldusage'

EPILOG: str = 'Learn more at https://github.com/untergeek/es-fieldusage'

HELP_OPTIONS: t.Dict[str, t.List[str]] = {'help_option_names': ['-h', '--help']}

OPTS: t.Dict[str, t.Dict[str, t.Any]] = {
    'report': {
        'help': 'Show a summary report',
        'default': True,
        'show_default': True,
    },
    'headers': {
        'help': 'Show block headers for un|accessed fields',
        'default': True,
        'show_default': True,
    },
    'accessed': {
        'help': 'Show accessed fields',
        'default': False,
        'show_default': True,
    },
    'unaccessed': {
        'help': 'Show unaccessed fields',
        'default': False,
        'show_default': True,
    },
    'counts': {
        'help': 'Show field access counts',
        'default': False,
        'show_default': True,
    },
    'delimiter': {
        'help': 'Value delimiter if access counts are shown',
        'type': str,
        'default': ',',
        'show_default': True,
    },
    'index': {
        'help': 'Create one file per index found',
        'default': False,
        'show_default': True,
    },
    'indexname': {
        'help': 'Write results to named ES index',
        'default': INDEXNAME,
        'show_default': True,
    },
    'filepath': {
        'help': 'Path where files will be written',
        'default': os.getcwd(),
        'show_default': True,
    },
    'prefix': {
        'help': 'Filename prefix',
        'default': 'es_fieldusage',
        'show_default': True,
    },
    'suffix': {
        'help': 'Filename suffix',
        'default': 'csv',
        'show_default': True,
    },
    'show_hidden': {'help': 'Show all options', 'is_flag': True, 'default': False},
}
