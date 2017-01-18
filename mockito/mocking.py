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

from collections import deque
import inspect
import functools

from . import invocation
from . import signature
from .mock_registry import mock_registry


__all__ = ['mock', 'Mock']


class _Dummy(object):
    def __getattr__(self, method_name):
        if self.__mock.strict:
            raise AttributeError('Unexpected')
        return self.__mock.__getattr__(method_name)

    def __call__(self, *args, **kwargs):
        return self.__getattr__('__call__')(*args, **kwargs)


class TestDouble(object):
    pass


def remembered_invocation_builder(mock, method_name, *args, **kwargs):
    invoc = invocation.RememberedInvocation(mock, method_name)
    return invoc(*args, **kwargs)


class Mock(TestDouble):
    def __init__(self, mocked_obj, strict=True, spec=None):
        self.mocked_obj = mocked_obj
        self.strict = strict
        self.spec = spec

        self.invocations = deque()
        self.stubbed_invocations = deque()

        self.original_methods = {}
        self._signatures_store = {}

    def __getattr__(self, method_name):
        return functools.partial(
            remembered_invocation_builder, self, method_name)

    def remember(self, invocation):
        self.invocations.appendleft(invocation)

    def finish_stubbing(self, stubbed_invocation):
        self.stubbed_invocations.appendleft(stubbed_invocation)


    # STUBBING

    def get_original_method(self, method_name):
        if isinstance(self.mocked_obj, _Dummy):
            return None
        if inspect.isclass(self.spec):
            return self.spec.__dict__.get(method_name)
        return getattr(self.spec, method_name)

    def set_method(self, method_name, new_method):
        setattr(self.mocked_obj, method_name, new_method)

    def replace_method(self, method_name, original_method):

        def new_mocked_method(*args, **kwargs):
            # we throw away the first argument, if it's either self or cls
            if (inspect.isclass(self.mocked_obj) and
                    not isinstance(original_method, staticmethod)):
                args = args[1:]

            # that is: invocation.RememberedInvocation(self, method_name)
            call = self.__getattr__(method_name)
            return call(*args, **kwargs)

        if isinstance(original_method, staticmethod):
            new_mocked_method = staticmethod(new_mocked_method)
        elif isinstance(original_method, classmethod):
            new_mocked_method = classmethod(new_mocked_method)

        self.set_method(method_name, new_mocked_method)

    def stub(self, method_name):
        try:
            self.original_methods[method_name]
        except KeyError:
            original_method = self.get_original_method(method_name)
            self.original_methods[method_name] = original_method

            self.replace_method(method_name, original_method)

    def unstub(self):
        while self.original_methods:
            method_name, original_method = self.original_methods.popitem()
            # If we mocked an instance, our mocked function will actually hide
            # the one on its class, so we delete it
            if (not inspect.isclass(self.mocked_obj) and
                    inspect.ismethod(original_method)):
                delattr(self.mocked_obj, method_name)
            else:
                self.set_method(method_name, original_method)

    # SPECCING

    def has_method(self, method_name):
        return hasattr(self.spec, method_name)

    def get_signature(self, method_name):
        try:
            return self._signatures_store[method_name]
        except KeyError:
            sig = signature.get_signature(self.spec, method_name)
            self._signatures_store[method_name] = sig
            return sig


def mock(config_or_spec=None, spec=None, strict=True):
    if type(config_or_spec) is dict:
        config = config_or_spec
    else:
        config = {}
        spec = config_or_spec

    if spec is None:
        strict = False

    theMock = Mock(None, strict=strict, spec=spec)

    class Dummy(_Dummy):
        __mock = theMock

    obj = Dummy()
    theMock.mocked_obj = obj
    for n, v in config.items():
        if inspect.isfunction(v):
            invocation.StubbedInvocation(theMock, n)(Ellipsis).thenAnswer(v)
        else:
            setattr(obj, n, v)
    mock_registry.register(obj, theMock)
    return obj
