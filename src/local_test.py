#!/usr/bin/env python
# pylint: disable=broad-except, no-value-for-parameter
"""
Wrapper for running es_fieldusage.cli but importing the module from the local file path
i.e., this must be executed from src.

The run_script.py script up one level from src imports from the installed module store.
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
