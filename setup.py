from setuptools import setup

import re
import ast


_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('mockito/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))


setup(name='mockito',
      version=version,
      packages=['mockito'],
      url='https://github.com/kaste/mockito-python',
      maintainer='herr.kaste',
      maintainer_email='herr.kaste@gmail.com',
      license='MIT',
      description='Spying framework',
      long_description=open('README.rst').read(),
      python_requires='>=3.7',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Topic :: Software Development :: Testing',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.10',
          'Programming Language :: Python :: 3.11',
          'Programming Language :: Python :: 3.12',
          'Programming Language :: Python :: 3.13',
          'Programming Language :: Python :: 3.14',
      ])
