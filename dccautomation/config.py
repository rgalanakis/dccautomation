import json
import sys

host = '127.0.0.1'
port = 9091

pyproc_tester_args = [
    sys.executable,
    '-c',
    'import dccautomation as d; d.start_server()'
]

mayaproc_test_args = [
    '/Applications/Autodesk/maya2015/Maya.app/Contents/bin/maya',
    '-command',
    'python("import dccautomation as d; d.start_server()")'
]

dumps = json.dumps
loads = json.loads

SUCCESS = 200
INVALID_METHOD = 400
UNHANDLED_ERROR = 503
