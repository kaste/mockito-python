#!/usr/bin/python2.4

import sys

if (len(sys.argv) > 1 and sys.argv[1] == 'uninstall'):
  print 'Uninstalling mockito...'
  
  exit(0)

if (len(sys.argv) > 1 and sys.argv[1] == 'verify'):
  print 'Verifying installation of mockito...'
  
  exit(0)
  
#TODO Write a task that tests installation  

from distutils.core import setup

setup(name='mockito',
      version='0.1.0',
      py_modules=['mockito/__init__', 'mockito/mockito', 'mockito/matchers', 'mockito/static_mocker', 'mockito/invocation', 'mockito/mock', 'mockito/verification'],
      url='http://code.google.com/p/mockito/wiki/MockitoForPython',
      maintainer='mockito maintainers',
      maintainer_email='mockito-python@googlegroups.com',
      license='MIT',
      description='Spying framework',
      long_description='Mockito is a spying framework based on Java library with the same name.'
)