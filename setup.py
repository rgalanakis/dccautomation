from setuptools import find_packages, setup

from dccautomation import version, __author__, __email__, __url__, __license__


setup(
    name='dccautomation',
    version=version,
    author=__author__,
    author_email=__email__,
    description="Library for external control or automation of "
                "any application that hosts a Python interpreter.",
    long_description=open('README.rst').read(),
    license=__license__,
    keywords='automation remote host dcc maya autodesk photoshop automate '
             'external control client server eval exec bootstrap handshake',
    url=__url__,
    packages=find_packages(),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
    install_requires=['pyzmq']
)
