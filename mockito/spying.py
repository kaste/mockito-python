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

'''Spying on real objects.'''

from invocation import RememberedProxyInvocation, VerifiableInvocation
from mocking import TestDouble

__all__ = ['spy']


def spy(original_object):
    return Spy(original_object)


class Spy(TestDouble):
    strict = True  # spies always have to check if method exists

    def __init__(self, original_object):
        self.original_object = original_object
        self.invocations = []
        self.verification = None

    def __getattr__(self, name):
        if self.verification:
            return VerifiableInvocation(self, name)
        else:
            return RememberedProxyInvocation(self, name)

    def remember(self, invocation):
        self.invocations.insert(0, invocation)

    def pull_verification(self):
        v = self.verification
        self.verification = None
        return v
