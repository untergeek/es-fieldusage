"""Command-line interface"""

import click
from es_client.commands import show_all_options
from es_client.defaults import OPTION_DEFAULTS
from es_client.helpers import config as escl
from es_client.helpers.logging import configure_logging
from es_fieldusage.defaults import EPILOG
from es_fieldusage.commands import file, show_indices, stdout
from es_fieldusage.version import __version__


# pylint: disable=R0913,R0914,W0613,W0622


@click.group(context_settings=escl.context_settings(), epilog=EPILOG)
@escl.options_from_dict(OPTION_DEFAULTS)
@click.version_option(__version__, '-v', '--version', prog_name="es-fieldusage")
@click.pass_context
def run(
    ctx,
    config,
    hosts,
    cloud_id,
    api_token,
    id,
    api_key,
    username,
    password,
    bearer_auth,
    opaque_id,
    request_timeout,
    http_compress,
    verify_certs,
    ca_certs,
    client_cert,
    client_key,
    ssl_assert_hostname,
    ssl_assert_fingerprint,
    ssl_version,
    master_only,
    skip_version_test,
    loglevel,
    logfile,
    logformat,
    blacklist,
):
    """Elasticsearch Index Field Usage Reporting Tool

    Sum all field query/request access for one or more indices using the Elastic
    Field Usage API (https://ela.st/usagestats)

    Generate a report at the command-line with the stdout command for all indices
    in INDEX_PATTERN:

    $ es-fieldusage stdout INDEX_PATTERN

    To avoid errors, be sure to encapsulate wildcards in single-quotes:

    $ es-fieldusage stdout 'index-*'
    """
    escl.get_config(ctx, quiet=False)
    configure_logging(ctx)
    escl.generate_configdict(ctx)


# This is now included with es_client. It works, so ignore weird typing issues
run.add_command(show_all_options)  # type: ignore

# Add the local subcommands
run.add_command(show_indices)
run.add_command(file)
# run.add_command(index)  # Not ready yet
run.add_command(stdout)
