#!/usr/bin/env python
# pylint: disable=broad-except, no-value-for-parameter
"""
Wrapper for running the command-line script from an installed module.

Because this script is up one level from src, it has to find the module
es_fieldusage.cli from installed modules. This makes it a good way to ensure
everything will work when installed.

To test development in progress, use the local_test.py script in src (and you
must be in src to execute)
"""
import sys
import click
from es_fieldusage.cli import run

if __name__ == '__main__':
    try:
        run()
    except RuntimeError as err:
        click.echo(f'{err}')
        sys.exit(1)
    except Exception as err:
        if 'ASCII' in str(err):
            click.echo(f'{err}')
            click.echo(__doc__)
