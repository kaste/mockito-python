#  Copyright (c) 2008-2016 Szczepan Faber, Serhiy Oplakanets, Herr Kaste
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#  THE SOFTWARE.

'''Matchers for stubbing and verifications.

Common matchers for use in stubbing and verifications.
'''

__all__ = ['any', 'contains', 'times']


class Matcher:
    def matches(self, arg):
        pass


class Any(Matcher):
    def __init__(self, wanted_type=None):
        self.wanted_type = wanted_type

    def matches(self, arg):
        if self.wanted_type:
            return isinstance(arg, self.wanted_type)
        else:
            return True

    def __repr__(self):
        return "<Any: %s>" % self.wanted_type


class Contains(Matcher):
    def __init__(self, sub):
        self.sub = sub

    def matches(self, arg):
        if not hasattr(arg, 'find'):
            return
        return self.sub and len(self.sub) > 0 and arg.find(self.sub) > -1

    def __repr__(self):
        return "<Contains: '%s'>" % self.sub


def any(wanted_type=None):
    """Matches any() argument OR any(SomeClass) argument

    Examples:
        when(mock).foo(any()).thenReturn(1)
        verify(mock).foo(any(int))
    """
    return Any(wanted_type)


def contains(sub):
    return Contains(sub)


def times(count):
    return count
