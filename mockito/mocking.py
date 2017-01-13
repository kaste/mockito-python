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

import inspect

from . import invocation
from . import signature
from .mock_registry import mock_registry


__all__ = ['mock', 'Mock']


class _Dummy(object):
    pass


class TestDouble(object):
    pass


class RememberedInvocationBuilder(object):
    def __init__(self, mock, method_name):
        self.mock = mock
        self.method_name = method_name

    def __call__(self, *params, **named_params):
        invoc = invocation.RememberedInvocation(self.mock, self.method_name)
        return invoc(*params, **named_params)

class State:
    STUBBING = 0
    CALLING = 1
    VERIFYING = 2

class Mock(TestDouble):
    def __init__(self, mocked_obj=None, strict=True, stub=False):
        self.mocked_obj = mocked_obj
        self.strict = strict
        self.stub_real_object = stub

        self.invocations = []
        self.stubbed_invocations = []

        self.original_methods = {}
        self._signatures_store = {}
        self._state = State.CALLING

        self.verification = None

    def __getattr__(self, method_name):
        if self._state is State.STUBBING:
            return invocation.StubbedInvocation(
                self, method_name, self.verification)

        elif self._state is State.VERIFYING:
            return invocation.VerifiableInvocation(self, method_name)

        elif self._state is State.CALLING:
            return RememberedInvocationBuilder(self, method_name)

    def remember(self, invocation):
        self.invocations.insert(0, invocation)

    def expect_stubbing(self, verification=None):
        self._state = State.STUBBING
        self.verification = verification

    def finish_stubbing(self, stubbed_invocation):
        self.stubbed_invocations.insert(0, stubbed_invocation)
        self.verification = None
        self._state = State.CALLING

    def expect_verifying(self, verification):
        self._state = State.VERIFYING
        self.verification = verification

    def pull_verification(self):
        v = self.verification
        self.verification = None
        self._state = State.CALLING
        return v

    def has_method(self, method_name):
        return hasattr(self.mocked_obj, method_name)

    def get_method(self, method_name):
        return self.mocked_obj.__dict__.get(method_name)

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
        if not self.stub_real_object:
            return

        try:
            self.original_methods[method_name]
        except KeyError:
            original_method = self.get_method(method_name)
            self.original_methods[method_name] = original_method

            self.replace_method(method_name, original_method)

    def unstub(self):
        while self.original_methods:
            method_name, original_method = self.original_methods.popitem()
            self.set_method(method_name, original_method)

    def get_signature(self, method_name):
        try:
            return self._signatures_store[method_name]
        except KeyError:
            sig = signature.get_signature(self.mocked_obj, method_name)
            self._signatures_store[method_name] = sig
            return sig


def mock(obj=None, strict=True, stub=False):
    if obj is None:
        return Mock(None, strict=False, stub=False)  # no spec, nothing to stub

    theMock = Mock(obj, strict=strict, stub=stub)
    mock_registry.register(theMock)
    return theMock
