#!/usr/bin/env python

import click
import logging
import json
from json.decoder import JSONDecodeError
import sys
import os
import datetime
import requests

from requests import Response
from learnosity_sdk.request import Init, DataApi

from pygments import highlight, lexers, formatters

# This is a public Learnosity Demos consumer
# XXX: never commit any other secret anywhere!
DEFAULT_CONSUMER_KEY='yis0TYCu7U9V4o7M'
DEFAULT_CONSUMER_SECRET='74c5fd430cf1242a527f6223aebd42d30464be22'

DEFAULT_API_AUTHOR_URL = 'https://authorapi{region}{env}.learnosity.com'
DEFAULT_API_AUTHOR_VERSION = 'latest'

DEFAULT_API_DATA_URL = 'https://data{region}{env}.learnosity.com'
DEFAULT_API_DATA_VERSION = 'v1'


# TODO: use credentials from environment/file
@click.group()
@click.option('--consumer-key', '-k',
              help=f'API key for desired consumer, defaults to {DEFAULT_CONSUMER_KEY}',
              default=DEFAULT_CONSUMER_KEY,
              envvar='LRN_CONSUMER_KEY', show_envvar=True)
@click.option('--consumer-secret', '-S',
              help=f'Secret associated with the consumer key, defaults to {DEFAULT_CONSUMER_SECRET}',
              default=DEFAULT_CONSUMER_SECRET,
              envvar='LRN_CONSUMER_SECRET', show_envvar=True)
# Requests
@click.option('--file', '-f', type=click.File('r'),
              help='File containing the JSON request',
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
# Environment
@click.option('--region', '-e',
              help='API region to target',
              envvar='LRN_REGION', show_envvar=True)
@click.option('--environment', '-e',
              help='API environment to target',
              envvar='LRN_ENVIRONMENT', show_envvar=True)
@click.option('--version', '-e',
              help='API version to target',
              envvar='LRN_VERSION', show_envvar=True)
# Logging
@click.option('--log-level', '-l', default='info',
              help='log level')
@click.option('--requests-log-level', '-L', default='warning',
              help='log level for the HTTP requests')
@click.pass_context
def cli(ctx,
        consumer_key, consumer_secret,
        file, request_json=None, dump_meta=False,
        environment=None, region=None, version=None,
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

    ctx.obj['region'] = region
    ctx.obj['environment'] = environment
    ctx.obj['version'] = version

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

    When not using a full URL, environment variables LRN_DEFAULT_VERSION, LRN_DEFAULT_REGION, and LRN_DEFAULT_ENV
    will be used to determine the location of the API to hit.

    '''
    ctx.ensure_object(dict)
    logger = ctx.obj['logger']
    consumer_key = ctx.obj['consumer_key']
    consumer_secret = ctx.obj['consumer_secret']

    author_request = _get_request(ctx)
    author_request = _add_user(author_request)
    endpoint_url = _build_endpoint_url(endpoint_url, DEFAULT_API_AUTHOR_URL, DEFAULT_API_AUTHOR_VERSION)
    action = _get_action(ctx)

    try:
        r = _send_www_encoded_request('author', endpoint_url, consumer_key, consumer_secret,
                                      author_request, action, logger)
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
@click.option('--reference', '-r', 'references',
              help='`reference` to request (can be used multiple times',
              multiple=True)
@click.option('--recurse', '-R', 'do_recurse', is_flag=True, default=False,
              help='Automatically recurse using the next token')
@click.pass_context
def data(ctx, endpoint_url, references=None,
         do_recurse=False):
    ''' Make a request to Data API.

    The endpoint_url can be:

    - a full URL: https://data.learnosity.com/v1/itembank/items

    - a REST path, with or without version:

      - /v1/itembank/items

      - /itembank/items

    When not using a full URL, environment variables LRN_DEFAULT_VERSION, LRN_DEFAULT_REGION, and LRN_DEFAULT_ENV
    will be used to determine the location of the API to hit.

    '''
    ctx.ensure_object(dict)
    logger = ctx.obj['logger']
    consumer_key = ctx.obj['consumer_key']
    consumer_secret = ctx.obj['consumer_secret']

    action = _get_action(ctx)
    data_request = _get_request(ctx)
    endpoint_url = _build_endpoint_url(endpoint_url, DEFAULT_API_DATA_URL, DEFAULT_API_DATA_VERSION)

    if len(references) > 0:
        if 'references' in data_request:
            logger.warning('Overriding `references` from request with references from the command line')
        data_request['references'] = references

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

def _get_env():
    return {
        'env': os.getenv('LRN_DEFAULT_ENV'),
        'region': os.getenv('LRN_DEFAULT_REGION'),
        'version': os.getenv('LRN_DEFAULT_VERSION'),
    }


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
                        region='', env=''):

    if region:
        region = f'-{region}'
    if env not in ['', 'prod', 'production']:
        env = f'.{env}'

    if not endpoint_url.startswith('http'):
        if not endpoint_url.startswith('/'):  # Prepend leading / if missing
            endpoint_url = f'/{endpoint_url}'
        if not endpoint_url.startswith('/v'):  # API version
            endpoint_url = f'/{version}{endpoint_url}'

        endpoint_url = default_url.format(region=region, env=env) + endpoint_url
    return endpoint_url


def _send_www_encoded_request(api, endpoint_url, consumer_key, consumer_secret,
                              request, action,
                              logger):
    security = _make_security_packet(consumer_key, consumer_secret)

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
        for r_iter in data_api.request_iter(endpoint_url, security, consumer_secret, request, action):
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
            logger.debug(f'Got {len(new_data)} new objects')
        meta['records'] = len(data)
        r = {
            'meta': meta,
            'data': data,
        }

    return r


def _make_security_packet(consumer_key, consumer_secret,
                               domain='localhost'):
    return {
        'consumer_key': consumer_key,
        'domain': domain,
        'timestamp': datetime.datetime.utcnow().strftime("%Y%m%d-%H%M")
    }


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
    elif stream is not sys.stderr:
        colorise = False

    outJson = json.dumps(data, indent=True)
    if colorise:
        outJson = highlight(outJson, lexers.JsonLexer(), formatters.TerminalFormatter())
    stream.write(outJson + '\n')
