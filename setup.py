#!/usr/bin/env python
# coding: utf-8

from setuptools import setup
import sys

extra = {}
if sys.version_info >= (3,):
    extra['use_2to3'] = True

setup(name='mockito',
      version='0.6.1',
      packages=['mockito', 'mockito_test'],
      url='https://github.com/kaste/mockito-python',
      maintainer='herr.kaste',
      maintainer_email='herr.kaste@gmail.com',
      license='MIT',
      description='Spying framework',
      long_description=open('README.rst').read(),
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Topic :: Software Development :: Testing',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3'
      ],
      test_suite='nose.collector',
      py_modules=['distribute_setup'],
      setup_requires=['nose'],
      **extra)
