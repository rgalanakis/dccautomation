"""
Allows remote control and automation of any process
that hosts a Python interpreter.
Right now it uses PyZMQ to communicate,
but this may be changed to HTTP or another pure-Python mechanism in the future
so there are no C dependencies which can be a pain to deploy for Maya.

Call :func:`dccautomation.start_server` in your application
(through a macro shelf button or whatever)
to start a server.

Then create a :class:`dccautomation.Client` in your client process
to communicate with it.
Use the ``eval_`` and ``exec_`` methods on it to eval and exec code
in your app,
returning the printed output and status code.

Things can be configured via a ``dccauto_config.py`` file that is importable.
See :mod:`dccautomation.config` for more information.

Use :class:`dccautomation.testcase.RemoteTestCase` as a base class
for tests that you want to execute in your app but run from pure Python
(such as if you run tests from your IDE, but they must be run in your DCC app).
"""

from .client import Client
from .server import start_server
