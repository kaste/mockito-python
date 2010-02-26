#!/usr/bin/env python
# coding: utf-8

from distribute_setup import use_setuptools
use_setuptools()

import sys
import os

if (len(sys.argv) > 1 and sys.argv[1] == 'test'):
  print("""
  Running tests against installed mockito...
  """)
  
  import shutil
  shutil.rmtree('build_test', True)
  shutil.copytree('mockito_test', 'build_test/mockito_test')
  
  sys.path[0] = os.path.join(sys.path[0], 'build_test', 'mockito_test')
  os.chdir(os.path.join('build_test', 'mockito_test'))
  
  import mockito_importer
  mockito_importer.imp = lambda : "don't really import anything..."
  
  import smart_test_runner
  smart_test_runner.run()
  
  exit(0)

if (len(sys.argv) == 1):
  print ("""
  1. Non-standard usage (not listed by --help):
    
    'setup.py test' runs tests against installed Mockito.
    You can use it to verify the installation: 
  
    setup.py test
    
  2. Standard usage:
  """)

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
      **extra
)

