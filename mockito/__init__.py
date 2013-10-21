#   Copyright (c) 2008-2013 Szczepan Faber, Serhiy Oplakanets, Herr Kaste
#
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#   of this software and associated documentation files (the "Software"), to deal
#   in the Software without restriction, including without limitation the rights
#   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#   copies of the Software, and to permit persons to whom the Software is
#   furnished to do so, subject to the following conditions:
#
#   The above copyright notice and this permission notice shall be included in
#   all copies or substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#   THE SOFTWARE.

'''Mockito is a Test Spy framework.'''


from mockito import mock, verify, verifyNoMoreInteractions, verifyZeroInteractions, when, unstub, ArgumentError
import inorder
from spying import spy
from verification import VerificationError

# Imports for compatibility
from mocking import Mock
from matchers import any, contains, times # use package import (``from mockito.matchers import any, contains``) instead of ``from mockito import any, contains``
from verification import never

__all__ = ['mock', 'spy', 'verify', 'verifyNoMoreInteractions', 'verifyZeroInteractions', 'inorder', 'when', 'unstub', 'VerificationError', 'ArgumentError',
           'Mock', # deprecated
           'any', # compatibility
           'contains', # compatibility
           'never', # compatibility
           'times' # deprecated
           ]
