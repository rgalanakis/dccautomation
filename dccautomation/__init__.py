version_info = 0, 0, 1
version = '.'.join([str(v) for v in version_info])
__version__ = version
__author__ = 'Rob Galanakis'
__email__ = 'rob.galanakis@gmail.com'
__url__ = 'https://github.com/rgalanakis/dccautomation'
__license__ = 'MIT'

from .bootstrap import start_server_process, ServerProc
from .client import (
    Client, Closed, InvalidMethod, Timeout, UnhandledError, UnhandledResponse
)
from .inproc import start_inproc_client, start_inproc_server
from .server import start_server, start_server_thread
from .testcase import RemoteTestCase
from . import configs
