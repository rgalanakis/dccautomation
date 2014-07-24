import os
import sys
import threading
import traceback

from . import common, compat, configs, utils


def _get_appsock_from_handshake(config, handshake_endpoint):
    app_info = utils.create_rep_socket_bound_to_random()

    handshake_sock = compat.MQ.socket(compat.MQ.REQ)
    handshake_sock.connect(handshake_endpoint)
    handshake_sock.send(config.dumps(app_info.endpoint))
    handshake_sock.recv()
    handshake_sock.close()

    return app_info.socket, app_info.endpoint


_execstate = {}


def eval_(source):
    return eval(source, _execstate, _execstate)


def exec_(source):
    return compat.exec_(source, _execstate, _execstate)


def start_server(env=None):
    """
    Starts the server and polls in a loop.
    The polling is blocking- eventually we may need to support
    non-blocking polling.
    """
    if env is None:
        env = os.environ
    configname = env.get(common.ENV_CONFIGNAME)
    if not configname:
        sys.exit('%s must be set.' % common.ENV_CONFIGNAME)
    config = configs.config_by_name(configname)

    handshake_endpoint = env.get(common.ENV_HANDSHAKE_ENDPOINT)
    if handshake_endpoint:
        sock, app_endpoint = _get_appsock_from_handshake(
            config, handshake_endpoint)
    else:
        app_endpoint = env.get(common.ENV_APP_ENDPOINT)
        if not app_endpoint:
            sys.exit('%s must be set if not using a handshake.'
                     % common.ENV_APP_ENDPOINT)
        sock = compat.MQ.socket(compat.MQ.REP)
        sock.bind(app_endpoint)

    logger = utils.logger(__name__, app_endpoint)
    exec_context = config.exec_context()
    keep_going = True
    logger.debug('Starting server loop.')
    while keep_going:
        recved = sock.recv()
        try:
            func, arg = config.loads(recved)
            logger.debug('recv: %s, %s', func, arg)
            code = common.SUCCESS
            value = None
            if func == 'exec':
                exec_context(exec_, arg)
            elif func == 'eval':
                value = exec_context(eval_, arg)
            elif func == 'close':
                keep_going = False
            else:
                code = common.INVALID_METHOD
                value = func
            response = {
                'code': code,
                'value': value
            }
        except Exception as ex:
            logger.debug('unhandled error occured!')
            response = {
                'code': common.UNHANDLED_ERROR,
                'errtype': ex.__class__.__name__,
                'traceback': ''.join(traceback.format_exc())
            }
        logger.debug('send: %s', response)
        sock.send(config.dumps(response))
    logger.debug('closing.')
    sock.close()
    logger.debug('server socket closed.')


def start_server_thread(env=None):
    """
    Starts the server on a daemon thread.
    """
    t = threading.Thread(
        target=start_server, args=[env], name='dccauto-srv-thread')
    t.daemon = True
    t.start()
