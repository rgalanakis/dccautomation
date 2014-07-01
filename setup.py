from setuptools import find_packages, setup


version_info = 0, 0, 1
version = '.'.join([str(v) for v in version_info])
__version__ = version
__author__ = 'Rob Galanakis'
__email__ = 'rob.galanakis@gmail.com'
__url__ = 'https://github.com/rgalanakis/dccautomation'
__license__ = 'MIT'


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
