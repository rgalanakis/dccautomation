import json

host = '127.0.0.1'
port = 9091

tester_proc_args = [
    '/Applications/Autodesk/maya2015/Maya.app/Contents/bin/maya',
    '-command',
    'python("import dccautomation as d; d.start_server()")'
]

dumps = json.dumps
loads = json.loads

SUCCESS = 200
INVALID_METHOD = 400
UNHANDLED_ERROR = 503
