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

'''Matchers for stubbing and verifications.

Common matchers for use in stubbing and verifications.
'''

import re


__all__ = [
    'and_', 'or_', 'not_',
    'eq', 'neq',
    'lt', 'lte',
    'gt', 'gte',
    'any', 'any_',
    'arg_that',
    'contains',
    'matches',
    'captor',
    'times',
    'args'
]

class _ArgsSentinel(object):
    def __repr__(self):
        return '*args'

ARGS_SENTINEL = _ArgsSentinel()
args = [ARGS_SENTINEL]


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


class ValueMatcher(Matcher):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.value)


class Eq(ValueMatcher):
    def matches(self, arg):
        return arg == self.value


class Neq(ValueMatcher):
    def matches(self, arg):
        return arg != self.value


class Lt(ValueMatcher):
    def matches(self, arg):
        return arg < self.value


class Lte(ValueMatcher):
    def matches(self, arg):
        return arg <= self.value


class Gt(ValueMatcher):
    def matches(self, arg):
        return arg > self.value


class Gte(ValueMatcher):
    def matches(self, arg):
        return arg >= self.value


class And(Matcher):
    def __init__(self, matchers):
        self.matchers = [
            matcher if isinstance(matcher, Matcher) else Eq(matcher)
            for matcher in matchers]

    def matches(self, arg):
        return all(matcher.matches(arg) for matcher in self.matchers)

    def __repr__(self):
        return "<And: %s>" % self.matchers


class Or(Matcher):
    def __init__(self, matchers):
        self.matchers = [
            matcher if isinstance(matcher, Matcher) else Eq(matcher)
            for matcher in matchers]

    def matches(self, arg):
        return __builtins__['any'](
            [matcher.matches(arg) for matcher in self.matchers]
        )

    def __repr__(self):
        return "<Or: %s>" % self.matchers


class Not(Matcher):
    def __init__(self, matcher):
        self.matcher = matcher if isinstance(matcher, Matcher) else Eq(matcher)

    def matches(self, arg):
        return not self.matcher.matches(arg)

    def __repr__(self):
        return "<Not: %s>" % self.matcher


class ArgThat(Matcher):
    def __init__(self, predicate):
        self.predicate = predicate

    def matches(self, arg):
        return self.predicate(arg)

    def __repr__(self):
        return "<ArgThat>"


class Contains(Matcher):
    def __init__(self, sub):
        self.sub = sub

    def matches(self, arg):
        if not hasattr(arg, 'find'):
            return
        return self.sub and len(self.sub) > 0 and arg.find(self.sub) > -1

    def __repr__(self):
        return "<Contains: '%s'>" % self.sub


class Matches(Matcher):
    def __init__(self, regex, flags=0):
        self.regex = re.compile(regex, flags)

    def matches(self, arg):
        if not isinstance(arg, str):
            return
        return self.regex.match(arg) is not None

    def __repr__(self):
        if self.regex.flags:
            return "<Matches: %s flags=%d>" % (self.regex.pattern,
                                               self.regex.flags)
        else:
            return "<Matches: %s>" % self.regex.pattern


class ArgumentCaptor(Matcher):
    def __init__(self, matcher=None):
        self.matcher = matcher or Any()
        self.value = None

    def matches(self, arg):
        result = self.matcher.matches(arg)
        if not result:
            return
        self.value = arg
        return True

    def __repr__(self):
        return "<ArgumentCaptor: matcher=%s value=%s>" % (
            repr(self.matcher), self.value,
        )


def any(wanted_type=None):
    """Matches any() argument OR any(SomeClass) argument

    Examples:
        when(mock).foo(any()).thenReturn(1)
        verify(mock).foo(any(int))
    """
    return Any(wanted_type)


any_ = any


def eq(value):
    """Matches particular value"""
    return Eq(value)


def neq(value):
    """Matches any but given value"""
    return Neq(value)


def lt(value):
    """Matches any value that is less than given value"""
    return Lt(value)


def lte(value):
    """Matches any value that is less than or equal to given value"""
    return Lte(value)


def gt(value):
    """Matches any value that is greater than given value"""
    return Gt(value)


def gte(value):
    """Matches any value that is greater than or equal to given value"""
    return Gte(value)


def and_(*matchers):
    """Matches if all given matchers match"""
    return And(matchers)


def or_(*matchers):
    """Matches if any given matcher match"""
    return Or(matchers)


def not_(matcher):
    """Matches if given matcher does not match"""
    return Not(matcher)


def arg_that(predicate):
    """Matches any argument for which predicate returns True

    Example:
        verify(mock).foo(arg_that(lambda arg: arg > 3 and arg < 7))
    """
    return ArgThat(predicate)


def contains(sub):
    """Matches any string containing given substring

    Example:
        mock.foo([120, 121, 122, 123])
        verify(mock).foo(contains(123))
    """
    return Contains(sub)


def matches(regex, flags=0):
    """Matches any string that matches given regex"""
    return Matches(regex, flags)


def captor(matcher=None):
    """Returns argument captor that captures value for further assertions

    Exmaple:
        arg_captor = captor(any(int))
        verify(mock).do_something(arg_captor)
        assert arg_captor.value == 123
    """
    return ArgumentCaptor(matcher)


def times(count):
    return count
