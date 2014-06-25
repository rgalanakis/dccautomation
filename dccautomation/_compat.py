import sys

try:
    import unittest2 as unittest
except ImportError:
    if sys.version_info < (2, 7):
        raise ImportError('unittest2 required for Python <= 2.6')
    import unittest
