#!/usr/bin/env python
# coding: utf-8

'''Mockito is a Test Spy framework.'''

__author__ = "Serhiy Oplakanets <serhiy@oplakanets.com>"
__copyright__ = "Copyright 2008-2010, Mockito Contributors"
__license__ = "MIT"
__maintainer__ = "Mockito Maintainers"
__email__ = "mockito-python@googlegroups.com"

from mockito import *

# Imports for compatibility
from mocking import Mock # use ``mock`` instead
from matchers import * # use package import (``from mockito.matchers import any, contains``) instead of ``from mockito import any, contains`` 
