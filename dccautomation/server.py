import os
import sys
import threading
import traceback
import zmq

from . import configs, statuscodes, utils


def _get_appsock_from_handshake(handshake_endpoint):
    app_sock = zmq.Context().socket(zmq.REP)
    host = 'tcp://127.0.0.1'
    app_port = app_sock.bind_to_random_port(host)
    app_endpoint = '%s:%s' % (host, app_port)

    handshake_sock = zmq.Context().socket(zmq.REQ)
    handshake_sock.connect(handshake_endpoint)
    handshake_sock.send(app_endpoint)
    handshake_sock.recv()
    handshake_sock.close()

    return app_sock


def _get_appsock_from_config(config):
    sock = zmq.Context().socket(zmq.REP)
    sock.bind('tcp://%s:%s' % (config.host, config.port))
    return sock


def start_server():
    configname = os.getenv(utils.ENV_CONFIGNAME)
    if not configname:
        sys.exit('%s must be set.' % utils.ENV_CONFIGNAME)
    config = configs.config_by_name(configname)

    handshake_endpoint = os.getenv(utils.ENV_HANDSHAKE)
    if handshake_endpoint:
        sock = _get_appsock_from_handshake(handshake_endpoint)
    else:
        sock = _get_appsock_from_config(configname)

    while True:
        recved = sock.recv()
        try:
            func, arg = config.loads(recved)
            code = statuscodes.SUCCESS
            response = None
            if func == 'exec':
                exec arg in globals(), globals()
            elif func == 'eval':
                response = eval(arg, globals(), globals())
            else:
                code = statuscodes.INVALID_METHOD
                response = func
            pickled = config.dumps({
                'code': code,
                'value': response
            })
        except Exception as ex:
            pickled = config.dumps({
                'code': statuscodes.UNHANDLED_ERROR,
                'errtype': ex.__class__.__name__,
                'traceback': ''.join(traceback.format_exc())
            })
        sock.send(pickled)


def start_server_thread():
    t = threading.Thread(target=start_server)
    t.start()
