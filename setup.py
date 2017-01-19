from setuptools import setup
import sys

import re
import ast


_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('mockito/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))


extra = {}
if sys.version_info >= (3,):
    extra['use_2to3'] = True

install_requires = ['funcsigs'] if sys.version_info < (3,) else []

setup(name='mockito',
      version=version,
      packages=['mockito', 'mockito.tests'],
      url='https://github.com/kaste/mockito-python',
      maintainer='herr.kaste',
      maintainer_email='herr.kaste@gmail.com',
      license='MIT',
      description='Spying framework',
      long_description=open('README.rst').read(),
      install_requires=install_requires,
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Topic :: Software Development :: Testing',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
      ],
      **extra)
