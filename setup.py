#!/usr/bin/env python
# coding: utf-8

from distribute_setup import use_setuptools
use_setuptools()

try:
  from setuptools import setup
except ImportError:
  from distutils.core import setup
import sys

extra = {}
if sys.version_info >= (3,):
  extra['use_2to3'] = True

setup(name='mockito',
      version='0.2.0',
      packages=['mockito'],
      url='http://code.google.com/p/mockito/wiki/MockitoForPython',
      download_url='http://bitbucket.org/szczepiq/mockito-python/downloads/',
      maintainer='mockito maintainers',
      maintainer_email='mockito-python@googlegroups.com',
      license='MIT',
      description='Spying framework',
      long_description='Mockito is a spying framework based on Java library with the same name.',
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Topic :: Software Development :: Testing'
                  ],
      test_loader = 'util.test:TestLoader',
      test_suite = 'mockito_test',
      **extra
)

