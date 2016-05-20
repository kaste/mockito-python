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

import matchers


class InvocationError(AttributeError):
    pass


class Invocation(object):
    def __init__(self, mock, method_name):
        self.method_name = method_name
        self.mock = mock
        self.verified = False
        self.verified_inorder = False
        self.params = ()
        self.named_params = {}
        self.answers = None
        self.strict = mock.strict

    def _remember_params(self, params, named_params):
        self.params = params
        self.named_params = named_params

    def __repr__(self):
        args = [repr(p) for p in self.params]
        kwargs = ["%s=%r" % (key, val)
                  for key, val in self.named_params.items()]
        params = ", ".join(args + kwargs)
        return "%s(%s)" % (self.method_name, params)

    def answer_first(self):
        return self.answers[0].answer() if self.answers is not None else None


class MatchingInvocation(Invocation):
    @staticmethod
    def compare(p1, p2):
        if isinstance(p1, matchers.Matcher):
            if not p1.matches(p2):
                return False
        elif p1 != p2:
            return False
        return True

    def matches(self, invocation):
        if self.method_name != invocation.method_name:
            return False
        if len(self.params) != len(invocation.params):
            return False
        if len(self.named_params) != len(invocation.named_params):
            return False
        if set(self.named_params.keys()) != set(invocation.named_params.keys()):
            return False

        for x, p1 in enumerate(self.params):
            if not self.compare(p1, invocation.params[x]):
                return False

        for x, p1 in self.named_params.iteritems():
            if not self.compare(p1, invocation.named_params[x]):
                return False

        return True


class RememberedInvocation(Invocation):
    def __call__(self, *params, **named_params):
        self._remember_params(params, named_params)
        self.mock.remember(self)

        for matching_invocation in self.mock.stubbed_invocations:
            if matching_invocation.matches(self):
                return matching_invocation.answer_first()

        if self.strict:
            stubbed_invocations = self.mock.stubbed_invocations or [None]
            raise InvocationError("""
You called

        %s,

which is not expected. Stubbed invocations are:

        %s

(Set strict to False to bypass this check.)
""" % (self, "\n    ".join(str(invoc) for invoc in stubbed_invocations)))

        return None


class RememberedProxyInvocation(Invocation):
    '''Remeber params and proxy to method of original object.

    Calls method on original object and returns it's return value.
    '''
    def __call__(self, *params, **named_params):
        self._remember_params(params, named_params)
        self.mock.remember(self)
        obj = self.mock.original_object
        try:
            method = getattr(obj, self.method_name)
        except AttributeError:
            raise AttributeError(
                "You tried to call method '%s' which '%s' instance does not "
                "have." % (self.method_name, obj.__class__.__name__))
        return method(*params, **named_params)


class VerifiableInvocation(MatchingInvocation):
    def __call__(self, *params, **named_params):
        self._remember_params(params, named_params)
        matched_invocations = []
        for invocation in self.mock.invocations:
            if self.matches(invocation):
                matched_invocations.append(invocation)

        verification = self.mock.pull_verification()
        verification.verify(self, len(matched_invocations))

        for invocation in matched_invocations:
            invocation.verified = True


class StubbedInvocation(MatchingInvocation):
    def ensure_mocked_object_has_method(self, method_name):
        if not self.mock.has_method(method_name):
            raise InvocationError(
                "You tried to stub a method '%s' the object (%s) doesn't "
                "have." % (method_name, self.mock.mocked_obj))

    def __call__(self, *params, **named_params):
        if self.mock.strict:
            self.ensure_mocked_object_has_method(self.method_name)
        self._remember_params(params, named_params)
        self.mock.stub(self.method_name)
        self.mock.finish_stubbing(self)
        return AnswerSelector(self)

    def stub_with(self, answer):
        if self.answers is None:
            self.answers = []
        self.answers.append(answer)


class AnswerSelector(object):
    def __init__(self, invocation):
        self.invocation = invocation
        self.answer = None

    def thenReturn(self, *return_values):
        for return_value in return_values:
            self.__then(Return(return_value))
        return self

    def thenRaise(self, *exceptions):
        for exception in exceptions:
            self.__then(Raise(exception))
        return self

    def thenAnswer(self, *callables):
        for callable in callables:
            self.__then(ReturnAnswer(self.invocation.mock, callable))
        return self

    def __then(self, answer):
        if not self.answer:
            self.answer = CompositeAnswer(answer)
            self.invocation.stub_with(self.answer)
        else:
            self.answer.add(answer)

class CompositeAnswer(object):
    def __init__(self, answer):
        self.answers = [answer]

    def add(self, answer):
        self.answers.insert(0, answer)

    def answer(self):
        if len(self.answers) > 1:
            a = self.answers.pop()
        else:
            a = self.answers[0]

        return a.answer()


class Raise(object):
    def __init__(self, exception):
        self.exception = exception

    def answer(self):
        raise self.exception


class Return(object):
    def __init__(self, return_value):
        self.return_value = return_value

    def answer(self):
        return self.return_value


class ReturnAnswer(object):
    def __init__(self, mock, answerable):
        self.answerable = answerable
        self.mock = mock

    def answer(self):
        current_invocation = self.mock.invocations[0]
        return self.answerable(*current_invocation.params, **current_invocation.named_params)

