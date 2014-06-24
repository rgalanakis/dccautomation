"""
Contains the :class:`Config` base class,
and a number of pre-defined subclasses for popular DCC applications
and platforms.
"""

import json
import sys


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


class CurrentPython(Config):
    port = 9092
    exe = sys.executable

    def popen_args(self):
        return [
            self.exe,
            '-c',
            'import dccautomation as d; d.start_server()'
        ]


class SystemPython(Config):
    port = 9093
    exe = 'python'


class Maya2015OSXConfig(Config):
    port = 9094

    def popen_args(self):
        return [
            '/Applications/Autodesk/maya2015/Maya.app/Contents/bin/maya',
            '-command',
            'python("import dccautomation as d; d.start_server()")'
        ]
