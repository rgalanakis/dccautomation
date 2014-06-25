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

    return app_info.socket


def start_server():
    configname = os.getenv(common.ENV_CONFIGNAME)
    if not configname:
        sys.exit('%s must be set.' % common.ENV_CONFIGNAME)
    config = configs.config_by_name(configname)

    handshake_endpoint = os.getenv(common.ENV_HANDSHAKE_ENDPOINT)
    if handshake_endpoint:
        sock = _get_appsock_from_handshake(handshake_endpoint)
    else:
        app_endpoint = os.getenv(common.ENV_APP_ENDPOINT)
        if not app_endpoint:
            sys.exit('%s must be set if not using a handshake.'
                     % common.ENV_APP_ENDPOINT)
        sock = zmq.Context().socket(zmq.REP)
        sock.bind(app_endpoint)

    keep_going = True
    while keep_going:
        recved = sock.recv()
        try:
            func, arg = config.loads(recved)
            code = common.SUCCESS
            response = None
            if func == 'exec':
                exec arg in globals(), globals()
            elif func == 'eval':
                response = eval(arg, globals(), globals())
            elif func == 'close':
                keep_going = False
            else:
                code = common.INVALID_METHOD
                response = func
            pickled = config.dumps({
                'code': code,
                'value': response
            })
        except Exception as ex:
            pickled = config.dumps({
                'code': common.UNHANDLED_ERROR,
                'errtype': ex.__class__.__name__,
                'traceback': ''.join(traceback.format_exc())
            })
        sock.send(pickled)
    sock.close()


def start_server_thread():
    t = threading.Thread(target=start_server)
    t.daemon = True
    t.start()
