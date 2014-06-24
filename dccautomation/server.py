import threading
import traceback
import zmq

from . import config, statuscodes


def start_server():
    sock = zmq.Context().socket(zmq.REP)
    sock.bind('tcp://%s:%s' % (config.host, config.port))
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
