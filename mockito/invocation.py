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

from . import matchers
from . import verification as verificationModule

import functools
import inspect
import sys
import types
try:
    from inspect import signature, Parameter
except ImportError:
    from funcsigs import signature, Parameter


PY3 = sys.version_info >= (3,)


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
        args = [repr(p) if p is not Ellipsis else '...'
                for p in self.params]
        kwargs = ["%s=%r" % (key, val)
                  if key is not matchers.KWARGS_SENTINEL else '**kwargs'
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

    def _remember_params(self, params, named_params):
        if Ellipsis in params and (params[-1] is not Ellipsis or named_params):
            raise TypeError('Ellipsis must be the last argument you specify.')

        if matchers.args in params:
            raise TypeError('args must be used as *args')

        if matchers.kwargs in params or matchers.KWARGS_SENTINEL in params:
            raise TypeError('kwargs must be used as **kwargs')

        self.params = params
        self.named_params = named_params


    def matches(self, invocation):  # noqa: C901 (too complex)
        if self.method_name != invocation.method_name:
            return False

        for x, p1 in enumerate(self.params):
            # assume Ellipsis is the last thing a user declares
            if p1 is Ellipsis:
                return True

            if p1 is matchers.ARGS_SENTINEL:
                break

            try:
                p2 = invocation.params[x]
            except IndexError:
                return False

            if not self.compare(p1, p2):
                return False
        else:
            if len(self.params) != len(invocation.params):
                return False

        for key, p1 in sorted(
                self.named_params.iteritems(),
                key=lambda (k, v): 1 if k is matchers.KWARGS_SENTINEL else 0):
            if key is matchers.KWARGS_SENTINEL:
                break

            try:
                p2 = invocation.named_params[key]
            except KeyError:
                return False

            if not self.compare(p1, p2):
                return False
        else:
            if len(self.named_params) != len(invocation.named_params):
                return False

        return True


class RememberedInvocation(Invocation):
    def __call__(self, *params, **named_params):
        self._remember_params(params, named_params)
        self.mock.remember(self)

        for matching_invocation in self.mock.stubbed_invocations:
            if matching_invocation.matches(self):
                matching_invocation.should_answer(self)
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


def positional_arguments(sig):
    return len([p for n, p in sig.parameters.items()
                if p.kind in (Parameter.POSITIONAL_ONLY,
                              Parameter.POSITIONAL_OR_KEYWORD)])

def has_var_keyword(sig):
    return any(p for n, p in sig.parameters.items()
               if p.kind is Parameter.VAR_KEYWORD)


class StubbedInvocation(MatchingInvocation):
    def __init__(self, mock, method_name, verification):
        super(StubbedInvocation, self).__init__(mock, method_name)
        self.verification = verification

    def ensure_mocked_object_has_method(self, method_name):
        if not self.mock.has_method(method_name):
            raise InvocationError(
                "You tried to stub a method '%s' the object (%s) doesn't "
                "have." % (method_name, self.mock.mocked_obj))

    def ensure_signature_matches(                 # noqa: C901 (too complex)
            self, method_name, args, kwargs):
        # Let's face it. If this doesn't work out, we have to do it the hard
        # way and reimplement something like `sig.bind` with our specific
        # need for `...`, `*args`, and `**kwargs` support.

        method = getattr(self.mock.mocked_obj, method_name)
        # Eat self for unbound methods bc signature doesn't do it
        if PY3:
            if (inspect.isclass(self.mock.mocked_obj) and
                    not inspect.ismethod(method) and
                    not isinstance(
                        self.mock.mocked_obj.__dict__.get(method_name),
                        staticmethod)):
                method = functools.partial(method, None)
        else:
            if (isinstance(method, types.UnboundMethodType) and
                    method.__self__ is None):
                method = functools.partial(method, None)

        try:
            sig = signature(method)
        except:
            return True

        ellipsis_provided = Ellipsis in args
        if ellipsis_provided:
            # Invariant: No args or kwargs allowed, but Ellipsis should consume
            # at least one var
            if not any(p for p in sig.parameters):
                raise TypeError("method doesn't take any arguments")

            has_kwargs = has_var_keyword(sig)
            # Ellipsis is always the last arg in args; it matches all keyword
            # arguments as well. So the strategy here is to strip off all
            # the keyword arguments from the signature, and do a partial
            # bind with the rest.
            params = [p for n, p in sig.parameters.items()
                      if p.kind not in (Parameter.KEYWORD_ONLY,
                                        Parameter.VAR_KEYWORD)]
            sig = sig.replace(parameters=params)
            # Ellipsis should fill at least one argument. We strip it off if
            # it can stand for a `kwargs` argument.
            sig.bind_partial(*(args[:-1] if has_kwargs else args))
        else:
            # `*args` should at least match one arg (t.i. not `*[]`), so we
            # keep it here. The value and its type is irrelevant in python.
            args_provided = matchers.ARGS_SENTINEL in args

            # If we find the `**kwargs` sentinel we must remove it, bc its
            # name cannot be matched against the sig.
            kwargs_provided = matchers.KWARGS_SENTINEL in kwargs
            if kwargs_provided:
                kwargs = kwargs.copy()
                kwargs.pop(matchers.KWARGS_SENTINEL)


            if args_provided or kwargs_provided:
                try:
                    sig.bind(*args, **kwargs)
                except TypeError as e:
                    error = str(e)
                    if 'too many positional arguments' in error:
                        raise TypeError('no argument for *args left')
                    if 'multiple values for argument' in error:
                        raise
                    if 'too many keyword arguments' in error:          # PY<3.5
                        raise
                    if 'got an unexpected keyword argument' in error:  # PY>3.5
                        raise

                else:
                    if kwargs_provided and not has_var_keyword(sig):
                        pos_args = positional_arguments(sig)
                        len_args = len(args) - int(args_provided)
                        len_kwargs = len(kwargs)
                        provided_args = len_args + len_kwargs
                        # Substitute at least one argument for the `**kwargs`,
                        # the user provided; t.i. do not allow kwargs to
                        # satisfy an empty `{}`.
                        if provided_args + 1 > pos_args:
                            raise TypeError(
                                'no keyword argument for **kwargs left')

            else:
                # Without Ellipsis and the other stuff this would really be
                # straight forward.
                sig.bind(*args, **kwargs)



    def __call__(self, *params, **named_params):
        if self.mock.strict:
            self.ensure_mocked_object_has_method(self.method_name)
            self.ensure_signature_matches(
                self.method_name, params, named_params)
        self._remember_params(params, named_params)

        self.mock.stub(self.method_name)
        self.mock.finish_stubbing(self)
        return AnswerSelector(self)

    def stub_with(self, answer):
        if self.answers is None:
            self.answers = []
        self.answers.append(answer)

    def should_answer(self, invocation):
        # type: (RememberedInvocation) -> None
        verification = self.verification
        if not verification:
            return

        actual_count = len([inv for inv in self.mock.invocations
                            if self.matches(inv)])

        if isinstance(verification, verificationModule.Times):
            if actual_count > verification.wanted_count:
                raise InvocationError(
                    "\nWanted times: %i, actual times: %i"
                    % (verification.wanted_count, actual_count))
        elif isinstance(verification, verificationModule.AtMost):
            if actual_count > verification.wanted_count:
                raise InvocationError(
                    "\nWanted at most: %i, actual times: %i"
                    % (verification.wanted_count, actual_count))
        elif isinstance(verification, verificationModule.Between):
            if actual_count > verification.wanted_to:
                raise InvocationError(
                    "\nWanted between: [%i, %i], actual times: %i"
                    % (verification.wanted_from,
                       verification.wanted_to,
                       actual_count))

        invocation.verified = True


    def verify(self):
        if not self.verification:
            return

        actual_count = len([
            invocation
            for invocation in self.mock.invocations
            if self.matches(invocation)])

        self.verification.verify(self, actual_count)




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
        return self.answerable(*current_invocation.params,
                               **current_invocation.named_params)

