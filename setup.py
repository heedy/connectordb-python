#!/usr/bin/env python

from setuptools import setup, find_packages


setup(name='ConnectorDB',
      version='0.3.0a1',  # The a.b of a.b.c follows connectordb version. c is the version of python. Remember to change __version__ in __init__
      description='ConnectorDB Python Interface',
      author='ConnectorDB team',
      license="MIT",
      author_email='support@connectordb.com',
      url='https://connectordb.com',
      packages=find_packages(exclude=['contrib', 'docs', '*_test']),
      classifiers=['Development Status :: 3 - Alpha',
                      'Intended Audience :: Developers',
                      'Intended Audience :: Science/Research',
                      'License :: OSI Approved :: MIT License',
                      'Programming Language :: Python :: 2.7'],
      install_requires=["requests", "websocket-client", "jsonschema"])
