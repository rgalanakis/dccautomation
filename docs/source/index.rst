.. conf.py copies the readme file over.
   It is in .gitignore, just in case.

.. include:: _copied_readme.rst

Useful API Members
==================

.. automodule:: dccautomation.configs

.. autoclass:: dccautomation.configs.Config
    :members:

.. autofunction:: dccautomation.configs.config_by_name

The :mod:`dccautomation.configs` module also contains a number of pre-defined
configs clients can use.

.. autoclass:: dccautomation.configs.CurrentPython
    :members:

.. autoclass:: dccautomation.configs.SystemPython
    :members:

.. autoclass:: dccautomation.configs.Maya2015OSX
    :members:

.. autoclass:: dccautomation.configs.Maya

Finally, the :class:`dccautomation.RemoteTestCase` class is very useful
for clients who wish to use ``dccautomation`` to run automated tests.

.. autoclass:: dccautomation.RemoteTestCase

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
