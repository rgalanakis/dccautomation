"""
Defines compatibility members for Python 2.6, Python3, etc.
"""

import sys

try:
    # noinspection PyPackageRequirements
    import unittest2 as unittest
except ImportError:  # pragma: no cover
    import unittest

if sys.version_info[0] == 2:
    # noinspection PyUnresolvedReferences
    import __builtin__ as builtins

    # noinspection PyShadowingBuiltins
    reload = reload

    # noinspection PyShadowingBuiltins
    def exec_(s, globals=None, locals=None):
        # noinspection PyRedundantParentheses
        exec (s) in globals, locals

else:
    # noinspection PyUnresolvedReferences
    import builtins

    import imp as _imp
    # noinspection PyShadowingBuiltins
    reload = _imp.reload

    # noinspection PyShadowingBuiltins
    def exec_(s, globals=None, locals=None):
        exec(s, globals, locals)
