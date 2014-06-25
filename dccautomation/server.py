import os
import sys
import threading
import traceback
import zmq

from . import common, configs, utils


def _get_appsock_from_handshake(handshake_endpoint):
    app_info = utils.create_rep_socket_bound_to_random()

    handshake_sock = zmq.Context().socket(zmq.REQ)
    handshake_sock.connect(handshake_endpoint)
    handshake_sock.send(app_info.endpoint)
    handshake_sock.recv()
    handshake_sock.close()

    return app_info.socket, app_info.endpoint


def _exec(s):
    exec s in globals(), globals()


def start_server():
    configname = os.getenv(common.ENV_CONFIGNAME)
    if not configname:
        sys.exit('%s must be set.' % common.ENV_CONFIGNAME)
    config = configs.config_by_name(configname)

    handshake_endpoint = os.getenv(common.ENV_HANDSHAKE_ENDPOINT)
    if handshake_endpoint:
        sock, app_endpoint = _get_appsock_from_handshake(handshake_endpoint)
    else:
        app_endpoint = os.getenv(common.ENV_APP_ENDPOINT)
        if not app_endpoint:
            sys.exit('%s must be set if not using a handshake.'
                     % common.ENV_APP_ENDPOINT)
        sock = zmq.Context().socket(zmq.REP)
        sock.bind(app_endpoint)

    logger = utils.logger(__name__, app_endpoint)
    exec_context = config.exec_context()
    keep_going = True
    while keep_going:
        recved = sock.recv()
        try:
            func, arg = config.loads(recved)
            logger.debug('recv: %s, %s', func, arg)
            code = common.SUCCESS
            value = None
            if func == 'exec':
                exec_context(_exec, arg)
            elif func == 'eval':
                value = exec_context(eval, arg, globals(), globals())
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
            response = {
                'code': common.UNHANDLED_ERROR,
                'errtype': ex.__class__.__name__,
                'traceback': ''.join(traceback.format_exc())
            }
        logger.debug('send: %s', response)
        sock.send(config.dumps(response))
    sock.close()


def start_server_thread():
    t = threading.Thread(target=start_server)
    t.daemon = True
    t.start()
