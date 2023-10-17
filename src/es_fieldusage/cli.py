"""Command-line interface"""
import click
from es_client.helpers import utils as escl
from es_fieldusage.defaults import EPILOG, get_context_settings
from es_fieldusage.helpers.utils import cli_opts
from es_fieldusage.commands import file, show_indices, stdout
from es_fieldusage.version import __version__

ONOFF = {'on': '', 'off': 'no-'}
click_opt_wrap = escl.option_wrapper()

# pylint: disable=unused-argument, redefined-builtin
@click.group(context_settings=get_context_settings(), epilog=EPILOG)
@click_opt_wrap(*escl.cli_opts('config'))
@click_opt_wrap(*escl.cli_opts('hosts'))
@click_opt_wrap(*escl.cli_opts('cloud_id'))
@click_opt_wrap(*escl.cli_opts('api_token'))
@click_opt_wrap(*escl.cli_opts('id'))
@click_opt_wrap(*escl.cli_opts('api_key'))
@click_opt_wrap(*escl.cli_opts('username'))
@click_opt_wrap(*escl.cli_opts('password'))
@click_opt_wrap(*escl.cli_opts('bearer_auth'))
@click_opt_wrap(*escl.cli_opts('opaque_id'))
@click_opt_wrap(*escl.cli_opts('request_timeout'))
@click_opt_wrap(*escl.cli_opts('http_compress', onoff=ONOFF))
@click_opt_wrap(*escl.cli_opts('verify_certs', onoff=ONOFF))
@click_opt_wrap(*escl.cli_opts('ca_certs'))
@click_opt_wrap(*escl.cli_opts('client_cert'))
@click_opt_wrap(*escl.cli_opts('client_key'))
@click_opt_wrap(*escl.cli_opts('ssl_assert_hostname'))
@click_opt_wrap(*escl.cli_opts('ssl_assert_fingerprint'))
@click_opt_wrap(*escl.cli_opts('ssl_version'))
@click_opt_wrap(*escl.cli_opts('master-only', onoff=ONOFF))
@click_opt_wrap(*escl.cli_opts('skip_version_test', onoff=ONOFF))
@click_opt_wrap(*cli_opts('loglevel'))
@click_opt_wrap(*cli_opts('logfile'))
@click_opt_wrap(*cli_opts('logformat'))
@click.version_option(__version__, '-v', '--version', prog_name="es-fieldusage")
@click.pass_context
def run(
    ctx, config, hosts, cloud_id, api_token, id, api_key, username, password, bearer_auth,
    opaque_id, request_timeout, http_compress, verify_certs, ca_certs, client_cert, client_key,
    ssl_assert_hostname, ssl_assert_fingerprint, ssl_version, master_only, skip_version_test,
    loglevel, logfile, logformat
):
    """Elasticsearch Index Field Usage Reporting Tool
    
    Sum all field query/request access for one or more indices using the Elastic Field Usage API
    (https://ela.st/usagestats)

    Generate a report at the command-line with the stdout command for all indices in INDEX_PATTERN:

    $ es-fieldusage stdout INDEX_PATTERN

    To avoid errors, be sure to encapsulate wildcards in single-quotes:

    $ es-fieldusage stdout 'index-*'
    """
    ctx.obj = {}

# Here is the ``show-all-options`` command, which does nothing other than set ``show=True`` for
# the hidden options in the top-level menu so they are exposed for the --help output.
@run.command(context_settings=get_context_settings(), short_help='Show all configuration options')
@click_opt_wrap(*escl.cli_opts('config'))
@click_opt_wrap(*escl.cli_opts('hosts'))
@click_opt_wrap(*escl.cli_opts('cloud_id'))
@click_opt_wrap(*escl.cli_opts('api_token'))
@click_opt_wrap(*escl.cli_opts('id'))
@click_opt_wrap(*escl.cli_opts('api_key'))
@click_opt_wrap(*escl.cli_opts('username'))
@click_opt_wrap(*escl.cli_opts('password'))
@click_opt_wrap(*escl.cli_opts('bearer_auth', show=True))
@click_opt_wrap(*escl.cli_opts('opaque_id', show=True))
@click_opt_wrap(*escl.cli_opts('request_timeout'))
@click_opt_wrap(*escl.cli_opts('http_compress', onoff=ONOFF, show=True))
@click_opt_wrap(*escl.cli_opts('verify_certs', onoff=ONOFF))
@click_opt_wrap(*escl.cli_opts('ca_certs'))
@click_opt_wrap(*escl.cli_opts('client_cert'))
@click_opt_wrap(*escl.cli_opts('client_key'))
@click_opt_wrap(*escl.cli_opts('ssl_assert_hostname', show=True))
@click_opt_wrap(*escl.cli_opts('ssl_assert_fingerprint', show=True))
@click_opt_wrap(*escl.cli_opts('ssl_version', show=True))
@click_opt_wrap(*escl.cli_opts('master-only', onoff=ONOFF, show=True))
@click_opt_wrap(*escl.cli_opts('skip_version_test', onoff=ONOFF, show=True))
@click_opt_wrap(*cli_opts('loglevel'))
@click_opt_wrap(*cli_opts('logfile'))
@click_opt_wrap(*cli_opts('logformat'))
@click.version_option(__version__, '-v', '--version', prog_name="es-fieldusage")
@click.pass_context
def show_all_options(
    ctx, config, hosts, cloud_id, api_token, id, api_key, username, password, bearer_auth,
    opaque_id, request_timeout, http_compress, verify_certs, ca_certs, client_cert, client_key,
    ssl_assert_hostname, ssl_assert_fingerprint, ssl_version, master_only, skip_version_test,
    loglevel, logfile, logformat
):
    """
    ALL CLIENT OPTIONS
    
    The following is the full list of settings available for configuring a connection using
    command-line options.
    """
    ctx = click.get_current_context()
    click.echo(ctx.get_help())
    ctx.exit()

# Add the subcommands
run.add_command(show_indices)
run.add_command(file)
run.add_command(stdout)
