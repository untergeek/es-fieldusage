"""Logging helpers"""
import sys
import logging
import click
import ecs_logging
from es_client.helpers.schemacheck import SchemaCheck
from es_client.helpers.utils import ensure_list, prune_nones
from es_fieldusage.defaults import config_logging
from es_fieldusage.helpers.utils import is_docker

class Whitelist(logging.Filter):
    """How to whitelist logs"""
    # pylint: disable=super-init-not-called
    def __init__(self, *whitelist):
        self.whitelist = [logging.Filter(name) for name in whitelist]

    def filter(self, record):
        return any(f.filter(record) for f in self.whitelist)

class Blacklist(Whitelist):
    """Blacklist monkey-patch of Whitelist"""
    def filter(self, record):
        return not Whitelist.filter(self, record)

class LogInfo:
    """Logging Class"""
    def __init__(self, cfg):
        """Class Setup

        :param cfg: The logging configuration
        :type: cfg: dict
        """
        cfg['loglevel'] = 'INFO' if not 'loglevel' in cfg else cfg['loglevel']
        cfg['logfile'] = None if not 'logfile' in cfg else cfg['logfile']
        cfg['logformat'] = 'default' if not 'logformat' in cfg else cfg['logformat']
        #: Attribute. The numeric equivalent of ``cfg['loglevel']``
        self.numeric_log_level = getattr(logging, cfg['loglevel'].upper(), None)
        #: Attribute. The logging format string to use.
        self.format_string = '%(asctime)s %(levelname)-9s %(message)s'

        if not isinstance(self.numeric_log_level, int):
            msg = f"Invalid log level: {cfg['loglevel']}"
            print(msg)
            raise ValueError(msg)

        #: Attribute. Which logging handler to use
        if is_docker():
            self.handler = logging.FileHandler('/proc/1/fd/1')
        else:
            self.handler = logging.StreamHandler(stream=sys.stdout)
        if cfg['logfile']:
            self.handler = logging.FileHandler(cfg['logfile'])

        if self.numeric_log_level == 10: # DEBUG
            self.format_string = (
                '%(asctime)s %(levelname)-9s %(name)22s %(funcName)22s:%(lineno)-4d %(message)s')

        if cfg['logformat'] == 'ecs':
            self.handler.setFormatter(ecs_logging.StdlibFormatter())
        else:
            self.handler.setFormatter(logging.Formatter(self.format_string))

def check_logging_config(config):
    """
    Ensure that the top-level key ``logging`` is in ``config`` before passing it to
    :py:class:`~.es_client.helpers.schemacheck.SchemaCheck` for value validation.

    :param config: Logging configuration data

    :type config: dict

    :returns: :py:class:`~.es_client.helpers.schemacheck.SchemaCheck` validated logging
        configuration.
    """

    if not isinstance(config, dict):
        click.echo(
            f'Must supply logging information as a dictionary. '
            f'You supplied: "{config}" which is "{type(config)}"'
            f'Using default logging values.'
        )
        log_settings = {}
    elif not 'logging' in config:
        # None provided. Use defaults.
        log_settings = {}
    else:
        if config['logging']:
            log_settings = prune_nones(config['logging'])
        else:
            log_settings = {}
    return SchemaCheck(
        log_settings, config_logging(), 'Logging Configuration', 'logging').result()

def set_logging(log_opts):
    """Configure global logging options

    :param log_opts: Logging configuration data

    :type log_opts: dict

    :rtype: None
    """
    # Set up logging
    loginfo = LogInfo(log_opts)
    logging.root.addHandler(loginfo.handler)
    logging.root.setLevel(loginfo.numeric_log_level)
    _ = logging.getLogger('redacter.cli')
    # Set up NullHandler() to handle nested elasticsearch8.trace Logger
    # instance in elasticsearch python client
    logging.getLogger('elasticsearch8.trace').addHandler(logging.NullHandler())
    if log_opts['blacklist']:
        for bl_entry in ensure_list(log_opts['blacklist']):
            for handler in logging.root.handlers:
                handler.addFilter(Blacklist(bl_entry))
