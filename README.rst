:orphan:

.. image:: https://travis-ci.org/rgalanakis/dccautomation.svg?branch=master
    :target: https://travis-ci.org/rgalanakis/dccautomation
    :alt: build status
    :align: right

.. image:: https://img.shields.io/coveralls/rgalanakis/dccautomation.svg
    :target: https://coveralls.io/r/rgalanakis/dccautomation
    :alt: coverage status
    :align: right

dccautomation: Take control of your programs
============================================

The `dccautomation library`_ facilitates the external control or automation
of any application that hosts a Python interpreter.
This is very useful when writing automated tests or systems against
a program, such as Autodesk Maya, that does not behave like a normal
Python interpreter.
A client process (usually a normal Python interpreter)
can connect to a server process (the application),
and have the Python interpreter execute and evaluate Python commands.

This is conceptually a simple and already served RPC mechanism,
but the complications of various DCC packages makes a package like
``dccautomation`` hugely beneficial, since it is both extensively
unit and production tested.

- **dccautomation** on GitHub: https://github.com/rgalanakis/dccautomation
- **dccautomation** on Read the Docs: http://dccautomation.readthedocs.org/
- **dccautomation** on Travis-CI: https://travis-ci.org/rgalanakis/dccautomation
- **dccautomation** on Coveralls: https://coveralls.io/r/rgalanakis/dccautomation

Usage
=====

Using ``dccautomation`` is very simple.
First, you must create or find a config for your application.
Then, you can run the ``dccautomation`` client and server
in one of two ways: with a paired client and server,
or with a server running on a well-known port.

Using a Config
--------------

Using a config (instance of the :class:`dccautomation.configs.Config` class)
is very simple.
First, look in the :mod:`dccautomation.configs` module for a configuration
for your application. New configurations are added regularly.

If you cannot find one there,
you can subclass :class:`dccautomation.configs.Config`
and override the necessary methods.

In either case, this is all the code you have to write to get
automation working.
You just pass this configuration around and let ``dccautomation``
do all the work.

Paired client and server
------------------------

The most common and useful way to use this library is to
bootstrap a server process and pair it with its own client.
This ensures nothing else can interfere with the server
(remember, the server is usually a very stateful application,
you wouldn't want state magically changing between client calls!).
This bootstrapping also allows you to have many server instances running,
because they will each be communicating over a unique port.
You can do this by running in your client process
(normally a standard Python interpreter)::

    import dccautomation
    cfg = MyAppConfig()
    svrproc = dccautomation.start_server_process(cfg)
    client = dccautomation.Client(svrproc)
    client.exec_('import mycode; mycode.do_stuff()')

Using a paired client and server is most useful when doing automated testing,
allowing you to run code that doesn't work in a normal Python interpreter.
It can also be useful when doing batch processing,
by starting up several instances of the application into a worker pool.

Well-known server and many clients
----------------------------------

Another useful scenario is to start a server on a background thread inside
of an already running application, using a well-known port.
Any number of clients can then connect to it.
You can do this by running the following in your application/server process::

    import dccautomation
    dccautomation.start_inproc_server(MyAppConfig(), 9023)

Then in your client process, you can run the following::

    import dccautomation
    client = inproc.start_inproc_client(MyAppConfig(), 9023)
    client.exec('import mycode; mycode.do_stuff()')

Note that your client and server need to know what port to communicate on
beforehand (we use ``9023`` in the previous examples).
This also means we can only have one server/application process running.

You can also set the ``DCCAUTO_INPROC_PORT`` environment variable
to set the port (usually before launching the process),
instead of hard-coding it to a number.
Do not pass in a port number, and the environment variable will be read.

Using a well-known server and one or more clients can be useful when
exploring how code works.
You can open up a GUI session of your application,
start a server,
run some code from the client process that manipulates the application,
and visually inspect the result afterwards.

It can also be useful when communicating between applications.
You can have Maya tell your game engine to update based on some change in Maya,
and you can have Maya update based on some change in the game engine.
To achieve this, you could do something like this::

    # In your game engine
    import dccautomation
    dccautomation.start_inproc_server(GameEngineConfig(), 9024)
    maya = dccautomation.start_inproc_client(MayaConfig(), 9025)
    maya.exec_('import pymel.core as pmc')

    # In Maya
    import dccautomation
    dccautomation.start_inproc_server(MayaConfig(), 9025)
    game = dccautomation.start_inproc_client(GameEngineConfig(), 9024)
    game.exec_('import leveleditor')

Writing tests that run in your application
==========================================

One of the major benefits of ``dccautomation`` is the
:class:`dccautomation.RemoteTestCase` class.
You can subclass this class,
and your test methods will run in your application.
This allows you, for example, to write normal-looking test code,
and then use standard Python tools (like ``nosetests``) to run your code.
For example, you could have the following test code::

    import dccautomation, my_configs
    try:
        import pymel.core as pmc
    except ImportError:
        pmc = None

    class SillyPymelTests(dccautomation.RemoteTestCase):
        config = my_configs.MayaConfig

        def testFindsActive(self):
            jnt = pmc.joint()
            self.assertEqual(jnt.type(), 'joint')

Then, you can run the tests in whatever fashion:
from your IDE, through ``nose`` or any test runner, whatever.
Under the hood, ``RemoteTestCase`` works some magic and your code is executed
inside your application.

Design
======

As stated previously, conceptually ``dccautomation`` is a simple RPC system.
In practice, setting up an RPC system using applications that host Python
is not trivial.
They have particular startup mechanics, are slow to start up,
have special environment setups and libraries,
and other considerations.
Many people need to write code in these environments,
but lose the benfit of modern tools or practices.
If you've ever tried to do Test Driven Development in Maya,
you have run into these issues!

So we created ``dccautomation`` to solve the needs of:

- Write automated tests that transparently run in custom applications.
- Have a way for a pure-Python application to use a custom application
  for special data processing
  (think something like an exporter that runs in a standard Python interpreter,
  that when you export will open up Maya
  behind the scenes to export the model).
- Parallel batch processing.

Internally, ``dccautomation`` uses PyZMQ. In the future,
the protocol mechanism may be configurable,
or changed to a pure-Python mechanism,
to eliminate comnpatibility issues.

Authors
=======

The primary author is Rob Galanakis, rob.galanakis@gmail.com.
The initial concepts of ``dccautomation`` were developed during my time
at CCP Games.
I give special thanks to my former colleagues there for proving that given the
right opportunity and tools, people can improve and excel.

.. _dccautomation library: http://dccautomation.readthedocs.org/en/latest/