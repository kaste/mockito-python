#!/usr/bin/python2.4

from distutils.core import setup

setup(name='mockito',
      version='0.1.0',
      py_modules=['src/mockito', 'src/matchers', 'src/static_mocker', 'src/invocation', 'src/mock', 'src/verification'],
      url='http://code.google.com/p/mockito/wiki/MockitoForPython',
      maintainer='mockito maintainers',
      maintainer_email='mockito-python@googlegroups.com',
      license='MIT',
      description='Spying framework',
      long_description='Mockito is a spying framework based on Java library with the same name.'
)