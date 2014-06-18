import atexit
import subprocess
import sys
import urlparse
import requests

from . import httpserver


PORT = '8081'


def start_server():
    args = [sys.executable, httpserver.__file__]
    proc = subprocess.Popen(args)
    atexit.register(proc.kill)
    return 'http://localhost:' + PORT


class HttpClient(object):
    def __init__(self, endpoint):
        self.endpoint = endpoint
        self.evalendpoint = urlparse.urljoin(self.endpoint, '/eval')

    def eval_(self, s):
        got = requests.post(self.evalendpoint, params={'s': s})
        if got.status_code != 200:

            raise RuntimeError(got.content)
        return got.json()['result']
