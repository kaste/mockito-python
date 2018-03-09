# Copyright (c) 2008-2016 Szczepan Faber, Serhiy Oplakanets, Herr Kaste
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

'''Mockito is a Test Spy framework.'''


from .mockito import (
    when, when2, patch, expect, unstub, clear, verify, verifyNoMoreInteractions,
    verifyZeroInteractions, verifyNoUnwantedInteractions,
    verifyStubbedInvocationsAreUsed,
    ArgumentError)
from . import inorder
from .spying import spy, spy2
from .mocking import mock
from .verification import VerificationError

from .matchers import *  # noqa: F403
from .verification import never

__version__ = '1.0.13-dev'

__all__ = ['mock', 'spy', 'spy2', 'when', 'when2', 'patch', 'expect', 'verify',
           'verifyNoMoreInteractions', 'verifyZeroInteractions',
           'verifyNoUnwantedInteractions', 'verifyStubbedInvocationsAreUsed',
           'inorder', 'unstub', 'clear',
           'VerificationError', 'ArgumentError',
           'any',       # compatibility
           'contains',  # compatibility
           'never',     # compatibility
           'times',     # deprecated
           ]
