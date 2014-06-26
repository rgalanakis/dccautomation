import sys
# noinspection PyUnresolvedReferences
import unittest  # For static analysis.

try:
    # noinspection PyPackageRequirements
    import unittest2 as unittest
except ImportError:  # pragma: no cover
    if sys.version_info < (2, 7):
        raise ImportError('unittest2 required for Python <= 2.6')
    import unittest
