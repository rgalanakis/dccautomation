import sys
# noinspection PyUnresolvedReferences
import unittest

if sys.version_info < (2, 7):
    try:
        # noinspection PyUnresolvedReferences
        import unittest2 as unittest
    except ImportError:
        pass
