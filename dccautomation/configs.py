"""
Contains the :class:`Config` base class,
and a number of pre-defined subclasses for popular DCC applications
and platforms.
You can get a config instance by its class name using
:func:`config_by_name`.
"""

import inspect
import json
import os
import sys


class Config(object):
    """
    Configuration for a controllable process.
    """

    def cfgname(self):
        """
        Return the configuration name.
        Used when many configs should share the same name
        (such as various OS flavors of a DCC app).
        """
        return type(self).__name__

    def dumps(self, data):
        """
        Dump the data into a string and return the string (bytes).
        Defaults to ``json.dumps(data).encode('utf-8')``.
        """
        return json.dumps(data).encode('utf-8')

    def loads(self, s):
        """
        Load data from a string (bytes).
        Defaults to ``json.loads(s.decode('utf-8'))``.
        """
        return json.loads(s.decode('utf-8'))

    def popen_args(self):
        """
        Return a list of command line arguments used to start a process
        and have it run an automation server.
        """
        raise NotImplementedError()

    def exec_context(self):
        """Return a callable will run exec and eval.
        Useful if the exec and eval must occur on a certain thread."""
        return lambda func, *a, **kw: func(*a, **kw)


class UnsupportedConfig(Config, Exception):
    def __init__(self, name):
        self.name = name
        Exception.__init__(self, 'Config %s is not yet supported.' % self.name)

    def __call__(self):
        raise self


def _get_first_valid(unsupported_msg, *configs):
    for cfg in configs:
        if os.path.exists(cfg.exe):
            return cfg
    return UnsupportedConfig(unsupported_msg)


class CurrentPython(Config):
    """
    The current executable.
    Assumed to be a valid Python interpreter.
    """
    exe = sys.executable

    def popen_args(self):
        return [
            self.exe,
            '-c',
            'import dccautomation as d; d.start_server()'
        ]


class SystemPython(Config):
    """
    The system python interpreter
    (what you'd get typing "python" from the command line).
    """
    exe = 'python'


class Maya2015OSX(Config):
    exe = '/Applications/Autodesk/maya2015/Maya.app/Contents/bin/maya'

    def cfgname(self):
        return 'Maya'

    def popen_args(self):
        return [
            self.exe,
            '-command',
            'python("import dccautomation as d; d.start_server()")'
        ]

    def exec_context(self):
        import maya
        if maya.cmds.about(batch=True):
            return lambda func, *a, **kw: func(*a, **kw)
        return maya.utils.executeInMainThreadWithResult


Maya = _get_first_valid('maya linux/windows', Maya2015OSX)


def config_by_name(name):
    for membername, cls in inspect.getmembers(
            sys.modules[__name__], inspect.isclass):
        if membername == name:
            return cls()
    raise UnsupportedConfig('No config found for %r' % name)
