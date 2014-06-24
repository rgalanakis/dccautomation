"""
Contains the :class:`Config` base class,
and a number of pre-defined subclasses for popular DCC applications
and platforms.
You can get a config instance by its class name using
:func:`conf_by_name`.
"""

import atexit
import inspect
import json
import os
import subprocess
import sys
import zmq


def _one_up_dir(f):
    return os.path.dirname(os.path.dirname(f))


def start_server_process(config):
    env = dict(os.environ)
    pythonpath = env.get('PYTHONPATH', '')
    env['PYTHONPATH'] = '{}{sep}{}{sep}{}'.format(
        pythonpath,
        _one_up_dir(__file__),
        _one_up_dir(zmq.__file__),
        sep=os.path.pathsep)
    proc = subprocess.Popen(config.popen_args(), env=env)
    atexit.register(proc.kill)
    return proc


class Config(object):
    """
    Configuration for a controllable process.
    The same configuration should be used by client and server.
    """
    host = '127.0.0.1'
    port = 9091

    def dumps(self, data):
        return json.dumps(data)

    def loads(self, s):
        return json.loads(s)

    def popen_args(self):
        """
        Return a list of command line arguments used to start a process
        and have it run an automation server.
        """
        raise NotImplementedError()


class UnsupportedConfig(Config):
    def __init__(self, name):
        self.name = name

    def __call__(self):
        raise RuntimeError('Config %s is not yet supported.' % self.name)


def _get_first_valid(unsupported_msg, *configs):
    for cfg in configs:
        if os.path.exists(cfg.exe):
            return cfg
    return UnsupportedConfig(unsupported_msg)


class CurrentPython(Config):
    port = 9092
    exe = sys.executable

    def popen_args(self):
        return [
            self.exe,
            '-c',
            'import dccautomation as d; d.start_server("CurrentPython")'
        ]


class SystemPython(Config):
    port = 9093
    exe = 'python'


class Maya2015OSX(Config):
    port = 9094
    exe = '/Applications/Autodesk/maya2015/Maya.app/Contents/bin/maya'

    def popen_args(self):
        return [
            self.exe,
            '-command',
            'python("import dccautomation as d; d.start_server(\\"Maya\\")")'
        ]


Maya = _get_first_valid('maya linux/windows', Maya2015OSX)


def config_by_name(classname):
    for membername, cls in inspect.getmembers(
            sys.modules[__name__], inspect.isclass):
        if membername == classname:
            return cls()
    raise RuntimeError('No config found for %r' % classname)
