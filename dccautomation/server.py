import threading
import traceback
import zmq

from . import config


def _start_server():
    sock = zmq.Context().socket(zmq.REP)
    sock.bind('tcp://%s:%s' % (config.host, config.port))
    while True:
        recved = sock.recv()
        try:
            func, arg = config.loads(recved)
            code = config.SUCCESS
            response = None
            if func == 'exec':
                exec arg in globals(), globals()
            elif func == 'eval':
                response = eval(arg, globals(), globals())
            else:
                code = config.INVALID_METHOD
                response = func
            pickled = config.dumps([code, response])
        except Exception:
            pickled = config.dumps([
                config.UNHANDLED_ERROR,
                ''.join(traceback.format_exc())])
        sock.send(pickled)


def start_server():
    t = threading.Thread(target=_start_server)
    t.start()
