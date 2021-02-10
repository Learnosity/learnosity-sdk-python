#!/usr/bin/env python

import click
import logging
import json
from json.decoder import JSONDecodeError
import sys
import os
import configparser
import datetime
import requests
from collections import OrderedDict

from requests import Response
from learnosity_sdk.request import Init, DataApi

from pygments import highlight, lexers, formatters

# This is a public Learnosity Demos consumer
# XXX: never commit any other secret anywhere!
DEFAULT_CONSUMER_KEY='yis0TYCu7U9V4o7M'
DEFAULT_CONSUMER_SECRET='74c5fd430cf1242a527f6223aebd42d30464be22'

DEFAULT_API_AUTHOR_URL = 'https://authorapi{region}{environment}.learnosity.com'
DEFAULT_API_AUTHOR_VERSION = 'latest'

DEFAULT_API_DATA_URL = 'https://data{region}{environment}.learnosity.com'
DEFAULT_API_DATA_VERSION = 'v1'

DEFAULT_API_QUESTIONS_URL = 'https://questions{region}{environment}.learnosity.com'
DEFAULT_API_QUESTIONS_VERSION = 'latest'

DEFAULT_API_REPORTS_URL = 'https://reports{region}{environment}.learnosity.com'
DEFAULT_API_REPORTS_VERSION = 'latest'

DOTDIR = os.path.expanduser('~') + '/.learnosity'
SHARED_CREDENTIALS_FILE = f'{DOTDIR}/credentials'
CONFIG_FILE = f'{DOTDIR}/config'

# TODO: use credentials from environment/file
@click.group()

@click.option('--consumer-key', '-k',
              help=f'API key for desired consumer, defaults to {DEFAULT_CONSUMER_KEY}',
              default=None,
              envvar='LRN_CONSUMER_KEY', show_envvar=True)
@click.option('--consumer-secret', '-S',
              help=f'Secret associated with the consumer key, defaults to {DEFAULT_CONSUMER_SECRET}',
              default=None,
              envvar='LRN_CONSUMER_SECRET', show_envvar=True)
# Requests
@click.option('--file', '-f', type=click.File('r'),
              help='File containing the JSON request.',
              default='-')
@click.option('--request-json', '-R', 'request_json',
              help='JSON body of the request to send,',
              metavar='JSON', default=None)
@click.option('--set', '-s', 'do_set', is_flag=True, default=False,
              help='Send a SET request')
@click.option('--update', '-u', 'do_update', is_flag=True, default=False,
              help='Send an UPDATE request')
@click.option('--dump-meta', '-m', is_flag=True, default=False,
              help='output meta object to stderr')
@click.option('--domain', '-d',
              help=f'Domain to use for web API requests',
              default='localhost')
# Environment
@click.option('--region', '-r',
              help='API region to target',
              envvar='LRN_REGION', show_envvar=True)
@click.option('--environment', '-e',
              help='API environment to target',
              envvar='LRN_ENVIRONMENT', show_envvar=True)
@click.option('--version', '-v',
              help='API version to target',
              envvar='LRN_VERSION', show_envvar=True)
# Configuration
@click.option('--shared-credentials-file', '-c', type=click.File('r'),
              help=f'Credentials file to use for profiles definition, defaults to {SHARED_CREDENTIALS_FILE}',
              default=None,
              envvar='LRN_SHARED_CREDENTIALS_FILE', show_envvar=True)
@click.option('--config-file', '-C', type=click.File('r'),
              help=f'Configuration file to use for profiles definition, defaults to {CONFIG_FILE}',
              default=None,
              envvar='LRN_CONFIG_FILE', show_envvar=True)
@click.option('--profile', '-p',
              help='Profile to use (provides default consumer key and secret from the credentials, as well as environment and region from the config)',
              envvar='LRN_PROFILE', show_envvar=True)
# Logging
@click.option('--log-level', '-l', default='info',
              help='log level')
@click.option('--requests-log-level', '-L', default='warning',
              help='log level for the HTTP requests')
@click.pass_context
def cli(ctx,
        consumer_key, consumer_secret,
        file, request_json=None, dump_meta=False,
        domain='localhost',
        environment=None, region=None, version=None,
        profile=None, shared_credentials_file=None, config_file=None,
        log_level='info', requests_log_level='warning',
        do_set=False, do_update=False,
        ):
    ''' Prepare and send requests to Learnosity APIs

        If neither --file nor --request-json are specified, the request will be read from STDIN. An empty input will be defaulted to {}, which a warning.
    '''
    ctx.ensure_object(dict)

    ctx.obj['consumer_key'] = consumer_key
    ctx.obj['consumer_secret'] = consumer_secret

    ctx.obj['file'] = file
    ctx.obj['request_json'] = request_json
    ctx.obj['do_set'] = do_set
    ctx.obj['do_update'] = do_update
    ctx.obj['dump_meta'] = dump_meta
    ctx.obj['domain'] = domain

    ctx.obj['region'] = region
    ctx.obj['environment'] = environment
    ctx.obj['version'] = version

    ctx.obj['shared_credentials_file'] = shared_credentials_file
    ctx.obj['config_file'] = config_file
    ctx.obj['profile'] = profile

    logging.basicConfig(
        format='%(asctime)s %(levelname)s:%(message)s',
        level=log_level.upper())

    requests_logger = logging.getLogger('urllib3')
    requests_logger.setLevel(requests_log_level.upper())
    requests_logger.propagate = True

    logger = logging.getLogger()
    ctx.obj['logger'] = logger


@cli.command()
@click.argument('endpoint_url')
@click.pass_context
def author(ctx, endpoint_url):
    ''' Make a request to Author API.

    The endpoint_url can be:

    - a full URL: https://authorapi.learnosity.com/v2020.2.LTS/itembank/items

    - a REST path, with or without version:

      - /latest-lts/itembank/items

      - /itembank/items

    '''
    return _get_api_response(ctx, 'author', endpoint_url, DEFAULT_API_AUTHOR_URL, DEFAULT_API_REPORTS_VERSION)


@cli.command()
@click.argument('endpoint_url')
@click.option('--limit', '-l', 'limit',
              help='Maximum `limit` of object to request at once')
@click.option('--reference', '-r', 'references',
              help='`reference` to request (can be used multiple times',
              multiple=True)
@click.option('--recurse', '-R', 'do_recurse', is_flag=True, default=False,
              help='Automatically recurse using the next token')
@click.pass_context
def data(ctx, endpoint_url, references=None, limit=None,
         do_recurse=False):
    ''' Make a request to Data API.

    The endpoint_url can be:

    - a full URL: https://data.learnosity.com/v1/itembank/items

    - a REST path, with or without version:

      - /v1/itembank/items

      - /itembank/items

    '''
    ctx.ensure_object(dict)
    logger = ctx.obj['logger']

    consumer_key, consumer_secret, version, region, environment = _get_profile(ctx, DEFAULT_API_DATA_VERSION)

    action = _get_action(ctx)
    data_request = _get_request(ctx)
    endpoint_url = _build_endpoint_url(endpoint_url, DEFAULT_API_DATA_URL, version, region, environment)

    if len(references) > 0:
        if 'references' in data_request:
            logger.warning('Overriding `references` in request with `--references` from the command line')
        data_request['references'] = references
    if limit:
        if 'limit' in data_request:
            logger.warning('Overriding `limit` in request with `--limit` from the command line')
        data_request['limit'] = limit

    logger.debug('Sending %s request to %s ...' %
                 (action.upper(), endpoint_url))
    try:
        r = _send_json_request(endpoint_url, consumer_key, consumer_secret, data_request, action,
                               logger, do_recurse)
    except Exception as e:
        logger.error('Exception sending request to %s: %s' %
                     (endpoint_url, e))
        return False

    response = _validate_response(ctx, r)
    if response is None:
        return False

    data = response['data']

    _output_json(data)
    return True


@cli.command()
@click.argument('endpoint_url')
@click.option('--user-id', '-u', required=True,
              help='`user_id` (to use in the security packet)')
@click.pass_context
def questions(ctx, endpoint_url, user_id):
    ''' Make a request to Questions API.

    The endpoint_url can be:

    - a full URL: https://questions.learnosity.com/v2021.1.LTS/questionresponses

    - a REST path, with or without version:

      - /latest-lts/questionresponses

      - /questionresponses

    Example:

    lrn-cli questions authenticate

    '''
    return _get_api_response(ctx, 'questions', endpoint_url,
                             DEFAULT_API_QUESTIONS_URL, DEFAULT_API_QUESTIONS_VERSION,
                             user_id)


@cli.command()
@click.argument('endpoint_url')
@click.pass_context
def reports(ctx, endpoint_url):
    ''' Make a request to Reports API.

    The endpoint_url can be:

    - a full URL: https://reports.learnosity.com/v2020.2.LTS/init

    - a REST path, with or without version:

      - /latest-lts/init

      - /init

    '''
    return _get_api_response(ctx, 'reports', endpoint_url, DEFAULT_API_REPORTS_URL, DEFAULT_API_REPORTS_VERSION)


def _get_profile(ctx, default_version=None):
    '''
    Returns profile information based on CLI option and config:
    * consumer_key,
    * consumer_secret,
    * version,
    * region,
    * environment
    '''
    logger = ctx.obj['logger']
    profile_name = ctx.obj['profile']


    # Changed in version 3.6: With the acceptance of PEP 468, order is retained for keyword
    # arguments passed to the OrderedDict constructor and its update() method.
    profile_params = OrderedDict(
        # credentials
        consumer_key=DEFAULT_CONSUMER_KEY,
        consumer_secret=DEFAULT_CONSUMER_SECRET,

        # config
        version=default_version,
        region='',
        environment=''
    )

    if profile_name:
        shared_credentials_file = ctx.obj['shared_credentials_file']
        if not shared_credentials_file:
            shared_credentials_file = open(SHARED_CREDENTIALS_FILE, 'r')
        credentials = configparser.ConfigParser()
        credentials.read_file(shared_credentials_file)

        if not ctx.obj['config_file']:
            try:
                ctx.obj['config_file'] = open(CONFIG_FILE, 'r')
            except FileNotFoundError:
                logger.debug(f'Config file not found: {CONFIG_FILE}')
        config_file = ctx.obj['config_file']

        # look for profile in config
        if config_file:
            config = configparser.ConfigParser()
            config.read_file(config_file)

            if profile_name not in config:
                logger.debug(f'Profile {profile_name} not found in config {config_file.name}')
            else:
                for key in [ 'version', 'region', 'environment' ]:
                    if key in config[profile_name]:
                        profile_params[key] = config[profile_name][key]
                # XXX: limited source_profile support: only allow to share credentials for now
                if 'source_profile' in config[profile_name]:
                    profile_name = config[profile_name]['source_profile']

        if profile_name not in credentials:
            logger.warning(f'Profile {profile_name} not found in credentials file {shared_credentials_file.name}, using learnosity-demos credentials...')
        else:
            for key in [ 'consumer_key', 'consumer_secret' ]:
                if key in credentials[profile_name]:
                    profile_params[key] = credentials[profile_name][key]

    # override everything with CLI/env config
    for key in profile_params.keys():
        if ctx.obj[key]:
            profile_params[key] = ctx.obj[key]

    return profile_params.values()


def _get_action(ctx):
    do_set = ctx.obj['do_set']
    do_update = ctx.obj['do_update']

    action = 'get'
    if do_set:
        action = 'set'

    if do_update:
        # XXX: Mutually exclusive options, This would be better implemented at the Click level
        if action != 'get':
            logger.error('Options --set and --update are mutually exclusive')
            exit(1)
        action = 'update'

    return action


def _get_request(ctx):
    file = ctx.obj['file']
    logger = ctx.obj['logger']
    request_json = ctx.obj['request_json']

    if request_json is not None:
        logger.debug('Using request JSON from command line argument')
        return json.loads(request_json)

    if file.isatty():
        # Make sure the user is aware they need to enter something
        logger.info(f'Reading request json from {file}...')
    else:
        logger.debug(f'Reading request json from {file}...')

    try:
        request = json.load(file)
    except JSONDecodeError as e:
        logger.warning(f'Invalid JSON ({e}), using empty request')
        request = {}

    return request


def _add_user(request):
    if 'user' in request:
        return

    request['user'] = {
        'id': 'lrn-cli',
        'firstname': 'Learnosity',
        'lastname': 'CLI',
        'email': 'lrn-cli@learnosity.com',
    }

    return request


def _build_endpoint_url(endpoint_url, default_url, version,
                        region='', environment=''):

    if region:
        region = f'-{region}'
    if environment not in ['', 'prod', 'production']:
        environment = f'.{environment}'

    if not endpoint_url.startswith('http'):
        if not endpoint_url.startswith('/'):  # Prepend leading / if missing
            endpoint_url = f'/{endpoint_url}'
        if not endpoint_url.startswith('/v'):  # API version
            endpoint_url = f'/{version}{endpoint_url}'

        endpoint_url = default_url.format(region=region, environment=environment) + endpoint_url
    return endpoint_url

def _get_api_response(ctx, api, endpoint_url, default_url, default_version, user_id=None):
    ctx.ensure_object(dict)
    logger = ctx.obj['logger']
    domain = ctx.obj['domain']

    consumer_key, consumer_secret, version, region, environment = _get_profile(ctx, default_version)

    api_request = _get_request(ctx)
    # XXX: This may not be relevant to all APIs, but it's fine as long as it doesn't break.
    api_request = _add_user(api_request)
    endpoint_url = _build_endpoint_url(endpoint_url, default_url, version, region, environment)
    action = _get_action(ctx)

    try:
        r = _send_www_encoded_request(api, endpoint_url, consumer_key, consumer_secret,
                                      api_request, action, logger, user_id, domain)
    except Exception as e:
        logger.error('Exception sending request to %s: %s' %
                     (endpoint_url, e))
        return False

    response = _validate_response(ctx, r)
    if response is None:
        return False

    data = response['data']

    _output_json(data)
    return True



def _send_www_encoded_request(api, endpoint_url, consumer_key, consumer_secret,
                              request, action,
                              logger, user_id=None, domain='localhost'):
    security = _make_security_packet(consumer_key, consumer_secret, user_id, domain)

    init = Init(api, security, consumer_secret, request)

    security['signature'] = init.generate_signature()

    form = {
        'action': action,
        'security': json.dumps(security),
        'request': init.generate_request_string(),
        'usrequest': init.generate_request_string(),
    }

    return requests.post(endpoint_url, data=form)


def _send_json_request(endpoint_url, consumer_key, consumer_secret,
                       request, action,
                       logger,
              do_recurse=False):
    data_api = DataApi()

    security = _make_security_packet(consumer_key, consumer_secret)

    if not do_recurse:
        r = data_api.request(endpoint_url, security, consumer_secret, request, action)
    else:
        meta = {
            '_comment': 'fake meta recreated by lrn-cli for failing initial recursive request',
            'status': 'false',
        }
        data = None
        logger.debug('Iterating through pages of data...')
        for i, r_iter in enumerate(data_api.request_iter(endpoint_url, security, consumer_secret, request, action)):
            meta = r_iter['meta']
            new_data = r_iter['data']
            if data is None:
                data = new_data
            elif type(data) is list:
                data += new_data
            elif type(data) is dict:
                data.update(new_data)
            else:
                raise Exception('Unexpected retun data type: not list or dict')
            logger.debug(f'Got page {i} with {len(new_data)} new objects')
        meta['records'] = len(data)
        r = {
            'meta': meta,
            'data': data,
        }

    return r


def _make_security_packet(consumer_key, consumer_secret, user_id=None,
                               domain='localhost'):
    security = {
        'consumer_key': consumer_key,
        'domain': domain,
        'timestamp': datetime.datetime.utcnow().strftime("%Y%m%d-%H%M")
    }

    if user_id:
        security['user_id'] = user_id

    return security


def _validate_response(ctx, r):
    logger = ctx.obj['logger']
    dump_meta = ctx.obj['dump_meta']

    try:
        response = _decode_response(r, logger, dump_meta)
    except Exception as e:
        logger.error('Exception decoding response: %s\nResponse text: %s' % (e, r.text))
        return None

    if not response['meta']['status']:
        logger.error('Incorrect status for request to %s: %s' %
                     (r.url, response['meta']['message']))
        return None
    return response


def _decode_response(response, logger, dump_meta=False):
    if type(response) == Response:
        if response.status_code != 200:
            logger.error('Error %d sending request to %s: %s' %
                         # TODO: try to extract an error message from r.json()
                         (response.status_code, response.url, response.text))
        response = response.json()
    if dump_meta and response['meta']:
        _output_json(response['meta'], sys.stderr)
    return response

def _output_json(data, stream=None):
    colorise = True
    if stream is None:
        stream = sys.stdout
    if not stream.isatty():
        colorise = False

    outJson = json.dumps(data, indent=True)
    if colorise:
        outJson = highlight(outJson, lexers.JsonLexer(), formatters.TerminalFormatter())
    stream.write(outJson + '\n')
