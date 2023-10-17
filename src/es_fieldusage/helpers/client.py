"""Client builder helper functions"""
import logging
from es_client.builder import Builder, ClientArgs, OtherArgs
from es_client.defaults import CLIENT_SETTINGS, VERSION_MAX, VERSION_MIN
from es_client.exceptions import ConfigurationError
from es_client.helpers import utils as escl
from es_fieldusage.exceptions import ClientException, ConfigurationException
from es_fieldusage.helpers.logging import check_logging_config, set_logging

def cloud_id_override(args, params, client_args):
    """
    If hosts are in the config file, but cloud_id is specified at the command-line,
    we need to remove the hosts parameter as cloud_id and hosts are mutually exclusive
    """
    logger = logging.getLogger(__name__)
    if params['cloud_id']:
        logger.info('cloud_id from command-line superseding configuration file settings')
        client_args.hosts = None
        args.pop('hosts', None)
    return args

def hosts_override(args, params, client_args):
    """
    If hosts are provided at the command-line, but cloud_id was in the config file, we need to
    remove the cloud_id parameter from the config file-based dictionary before merging
    """
    logger = logging.getLogger(__name__)
    if params['hosts']:
        logger.info('hosts from command-line superseding configuration file settings')
        client_args.hosts = None
        client_args.cloud_id = None
        args.pop('cloud_id', None)
    return args

def configure_logging(params, config):
    """Configure logging based on params and config

    Values in params will override anything set in config
    """
    # Check for log settings from config file
    init_logcfg = check_logging_config(config)

    # Override anything with options from the command-line
    if params['loglevel']:
        init_logcfg['loglevel'] = params['loglevel']
    if params['logfile']:
        init_logcfg['logfile'] = params['logfile']
    if params['logformat']:
        init_logcfg['logformat'] = params['logformat']
    # Now enable logging with the merged settings
    set_logging(check_logging_config({'logging': init_logcfg}))

def get_arg_objects(config):
    """Return initial tuple of ClientArgs, OtherArgs
    
    They will be either empty, or with values from config
    """
    client_args = ClientArgs()
    other_args = OtherArgs()
    if config:
        validated_config = escl.check_config(config)
        client_args.update_settings(validated_config['client'])
        other_args.update_settings(validated_config['other_settings'])
    return client_args, other_args

def get_client(
    configdict=None, configfile=None, autoconnect=False, version_min=VERSION_MIN,
    version_max=VERSION_MAX):
    """Get an Elasticsearch Client using :py:class:`es_client.Builder`

    Build a client out of settings from `configfile` or `configdict`
    If neither `configfile` nor `configdict` is provided, empty defaults will be used.
    If both are provided, `configdict` will be used, and `configfile` ignored.

    :param configdict: A configuration dictionary
    :param configfile: A configuration file
    :param autoconnect: Connect to client automatically
    :param verion_min: Minimum acceptable version of Elasticsearch (major, minor, patch)
    :param verion_max: Maximum acceptable version of Elasticsearch (major, minor, patch)

    :type configdict: dict
    :type configfile: str
    :type autoconnect: bool
    :type version_min: tuple
    :type version_max: tuple

    :returns: A client connection object
    :rtype: :py:class:`~.elasticsearch.Elasticsearch`
    """
    logger = logging.getLogger(__name__)
    logger.debug('Creating client object and testing connection')

    builder = Builder(
        configdict=configdict, configfile=configfile, autoconnect=autoconnect,
        version_min=version_min, version_max=version_max
    )

    try:
        builder.connect()
    except Exception as exc:
        logger.critical('Unable to establish client connection to Elasticsearch!')
        logger.critical('Exception encountered: %s', exc)
        raise ClientException from exc

    return builder.client

def get_config(params):
    """If params['config'] is a valid path, return the validated dictionary from the YAML"""
    config = {'config':{}} # Set a default empty value
    if params['config']:
        config = escl.get_yaml(params['config'])
    return config

def get_hosts(params):
    """Return hostlist for client object"""
    logger = logging.getLogger(__name__)
    hostslist = []
    if params['hosts']:
        for host in list(params['hosts']):
            try:
                hostslist.append(escl.verify_url_schema(host))
            except ConfigurationError as err:
                logger.error('Incorrect URL Schema: %s', err)
                raise ConfigurationException from err
    else:
        hostslist = None
    return hostslist

def override_client_args(params, client_args):
    """Override client_args settings with values from params"""
    # cli_client = escl.prune_nones({
    #     'hosts': get_hosts(params),
    #     'cloud_id': params['cloud_id'],
    #     'bearer_auth': params['bearer_auth'],
    #     'opaque_id': params['opaque_id'],
    #     'request_timeout': params['request_timeout'],
    #     'http_compress': params['http_compress'],
    #     'verify_certs': params['verify_certs'],
    #     'ca_certs': params['ca_certs'],
    #     'client_cert': params['client_cert'],
    #     'client_key': params['client_key'],
    #     'ssl_assert_hostname': params['ssl_assert_hostname'],
    #     'ssl_assert_fingerprint': params['ssl_assert_fingerprint'],
    #     'ssl_version': params['ssl_version']
    # })
    args = {}
    for key, value in params.items():
        if key in CLIENT_SETTINGS:
            if key == 'hosts':
                args[key] = get_hosts(params)
            elif value is not None:
                args[key] = value
    args = cloud_id_override(args, params, client_args)
    args = hosts_override(args, params, client_args)
    args = escl.prune_nones(args)
    # Update the object if we have settings to override after pruning None values
    if args:
        client_args.update_settings(args)

def override_other_args(params, other_args):
    """Override other_args settings with values from params"""
    args = escl.prune_nones({
        'master_only': params['master_only'],
        'skip_version_test': params['skip_version_test'],
        'username': params['username'],
        'password': params['password'],
        'api_key': {
            'id': params['id'],
            'api_key': params['api_key'],
            'token': params['api_token'],
        }
    })

    # Remove `api_key` root key if `id` and `api_key` and `token` are all None
    if params['id'] is None and params['api_key'] is None and params['api_token'] is None:
        del args['api_key']

    if args:
        other_args.update_settings(args)

def get_args(params):
    """Return ClientArgs, OtherArgs tuple from params"""
    config = get_config(params)
    configure_logging(params, config)
    client_args, other_args = get_arg_objects(config)
    override_client_args(params, client_args)
    override_other_args(params, client_args)

    return client_args, other_args
