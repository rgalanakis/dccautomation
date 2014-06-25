from setuptools import find_packages, setup

# from dccautomation import version, __author__, __email__, __url__, __license__
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
    description="TBD",
    long_description=open('README.rst').read(),
    license=__license__,
    keywords='TBD TBD',
    url=__url__,
    packages=find_packages(),
    classifiers=[
        # 'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        # 'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        # 'Programming Language :: Python :: 3',
    ],
    install_requires=['pyzmq']
)
