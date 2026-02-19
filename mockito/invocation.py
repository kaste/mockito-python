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

from __future__ import annotations
from abc import ABC
import os
import inspect
import operator
from collections import deque

from . import matchers, signature
from . import verification as verificationModule
from .utils import contains_strict

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Callable, NoReturn, Self, TypeVar, TYPE_CHECKING
    from .mocking import Mock
    T = TypeVar('T')


class InvocationError(AttributeError):
    pass

class AnswerError(AttributeError):
    pass


__tracebackhide__ = operator.methodcaller(
    "errisinstance",
    (InvocationError, verificationModule.VerificationError)
)


class Invocation(object):
    def __init__(self, mock: Mock, method_name: str) -> None:
        self.mock = mock
        self.method_name = method_name
        self.strict = mock.strict

        self.params: tuple[Any, ...] = ()
        self.named_params: dict[str, Any] = {}

    def _remember_params(self, params: tuple, named_params: dict) -> None:
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


class RealInvocation(Invocation, ABC):
    def __init__(self, mock: Mock, method_name: str) -> None:
        super(RealInvocation, self).__init__(mock, method_name)
        self.verified = False
        self.verified_inorder = False


class RememberedInvocation(RealInvocation):
    def ensure_mocked_object_has_method(self, method_name: str) -> None:
        if not self.mock.has_method(method_name):
            raise InvocationError(
                "You tried to call a method '%s' the object (%s) doesn't "
                "have." % (method_name, self.mock.mocked_obj))

    def ensure_signature_matches(
        self, method_name: str, args: tuple, kwargs: dict
    ) -> None:
        sig = self.mock.get_signature(method_name)
        if not sig:
            return

        signature.match_signature(sig, args, kwargs)

    def __call__(self, *params: Any, **named_params: Any) -> Any | None:
        if self.mock.eat_self(self.method_name):
            params_without_first_arg = params[1:]
        else:
            params_without_first_arg = params
        if self.strict:
            self.ensure_mocked_object_has_method(self.method_name)
            self.ensure_signature_matches(
                self.method_name, params_without_first_arg, named_params)

        self._remember_params(params_without_first_arg, named_params)
        self.mock.remember(self)

        for matching_invocation in self.mock.stubbed_invocations:
            if matching_invocation.matches(self):
                matching_invocation.should_answer(self)
                matching_invocation.capture_arguments(self)
                return matching_invocation.answer_first(
                    *params, **named_params)

        if self.strict:
            stubbed_invocations = [
                invoc
                for invoc in self.mock.stubbed_invocations
                if invoc.method_name == self.method_name
            ]
            raise InvocationError(
                """
Called but not expected:

    %s

Stubbed invocations are:

    %s

"""
                % (
                    self,
                    "\n    ".join(
                        str(invoc) for invoc in reversed(stubbed_invocations)
                    )
                )
            )

        return None


class RememberedPropertyAccess(RememberedInvocation):
    def ensure_mocked_object_has_method(self, method_name):
        return True

    def ensure_signature_matches(self, method_name, args, kwargs):
        return True


class RememberedProxyInvocation(RealInvocation):
    """Remember params and proxy to method of original object.

    Calls method on original object and returns it's return value.
    """
    def __call__(self, *params: Any, **named_params: Any) -> Any:
        self._remember_params(params, named_params)
        self.mock.remember(self)
        obj = self.mock.spec
        try:
            method = getattr(obj, self.method_name)
        except AttributeError:
            raise AttributeError(
                "You tried to call method '%s' which '%s' instance does not "
                "have." % (self.method_name, obj))
        return method(*params, **named_params)



class MatchingInvocation(Invocation, ABC):
    """
    Abstract base class for `RememberedInvocation` and `VerifiableInvocation`.

    Mainly implements `matches` which is used to compare calling signatures
    where placeholders and matchers (like `any()` or `Ellipsis`) are
    interpreted. Here, `self` can contain such special placeholders which then
    consume multiple arguments of the (other) `invocation`.

    """
    @staticmethod
    def compare(p1, p2):
        if isinstance(p1, matchers.Matcher):
            if not p1.matches(p2):
                return False
        elif p1 != p2:
            return False
        return True

    def capture_arguments(self, invocation: RealInvocation) -> None:
        """Capture arguments of `invocation` into "capturing" matchers of self.

        This is used in conjunction with "capturing" matchers like
        `ArgumentCaptor`, e.g. `captor`.

        Imagine a `when(obj).method(captor).thenReturn()` configuration.  Now,
        when `obj.method("foo")` is called, "foo" will be passed to
        `captor.capture_value`.

        """
        for x, p1 in enumerate(self.params):
            if isinstance(p1, matchers.Capturing):
                try:
                    p2 = invocation.params[x]
                except IndexError:
                    continue

                p1.capture_value(p2)

        for key, p1 in self.named_params.items():
            if isinstance(p1, matchers.Capturing):
                try:
                    p2 = invocation.named_params[key]
                except KeyError:
                    continue

                p1.capture_value(p2)


    def _remember_params(self, params: tuple, named_params: dict) -> None:
        if (
            contains_strict(params, Ellipsis)
            and (params[-1] is not Ellipsis or named_params)
        ):
            raise TypeError('Ellipsis must be the last argument you specify.')

        if contains_strict(params, matchers.args):
            raise TypeError('args must be used as *args')

        if (
            contains_strict(params, matchers.kwargs)
            or contains_strict(params, matchers.KWARGS_SENTINEL)
        ):
            raise TypeError('kwargs must be used as **kwargs')

        def wrap(p):
            if p is any or p is matchers.any_:
                return matchers.any_()
            return p

        self.params = tuple(wrap(p) for p in params)
        self.named_params = {k: wrap(v) for k, v in named_params.items()}

    # Note: matches(a, b) does not imply matches(b, a) because
    # the left side might contain wildcards (like Ellipsis) or matchers.
    # In its current form the right side is a concrete call signature.
    def matches(self, invocation: Invocation) -> bool:  # noqa: C901, E501  (too complex)
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
            self.named_params.items(),
            key=lambda k_v: 1 if k_v[0] is matchers.KWARGS_SENTINEL else 0
        ):
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


class VerifiableInvocation(MatchingInvocation):
    """
    Denotes the function or method signature after `verify` is called.

    I.e.  verify(obj).method(arg1, ...)
                      ^^^^^^^^^^^^^^^^^  VerifiableInvocation denotes this part

    The constructor takes the mock object, which is the registered `Mock` for
    the `obj` in the previous examples, the method name (in the example:
    `method`), and the verification mode (i.e. `verificationModule.Times(1)`).

    In the immediately following `__call__` call, the arguments (`args1, ...`)
    are captured and verified.  For `verify` `__call__` ends the verification
    process, there is no third fluent interface.

    Both calls, `__init__` plus `__call__`, encapsulate a method or function
    call.  But the `__call__` is essentially virtual and can contain
    placeholders and matchers.
    """
    def __init__(
        self,
        mock: Mock,
        method_name: str,
        verification: verificationModule.VerificationMode
    ) -> None:
        super(VerifiableInvocation, self).__init__(mock, method_name)
        self.verification = verification
        self.verification_allows_zero_matches = \
            verification_has_lower_bound_of_zero(self.verification)

    def __call__(self, *params: Any, **named_params: Any) -> None:
        self._remember_params(params, named_params)
        matched_invocations = []
        for invocation in self.mock.invocations:
            if self.matches(invocation):
                self.capture_arguments(invocation)
                matched_invocations.append(invocation)

        self.verification.verify(self, len(matched_invocations))

        # check (real) invocations as verified
        for invocation in matched_invocations:
            invocation.verified = True

        self.maybe_check_stubs_as_used()

    def maybe_check_stubs_as_used(self) -> None:
        """Mark matching stubs as used for explicit zero-lower-bound verifies.

        This is important for follow-up global checks like
        ``verifyStubbedInvocationsAreUsed`` and
        ``ensureNoUnverifiedInteractions``: once a call pattern was explicitly
        verified (including the case where the expected count is zero), those
        checks should not fail only because the corresponding stub has factual
        usage count ``0``.

        In other words, such tests are about verifying *absence* of matching
        invocations, not about requiring that the stub was exercised.
        """
        if self.verification_allows_zero_matches:
            for stub in self.mock.stubbed_invocations:
                # Remember: matches(a, b) does not imply matches(b, a)
                # (see above!), so we check for both
                if stub.matches(self) or self.matches(stub):
                    stub.allow_zero_invocations = True


def verification_has_lower_bound_of_zero(
    verification: verificationModule.VerificationMode | None
) -> bool:
    if (
        isinstance(verification, verificationModule.Times)
        and verification.wanted_count == 0
    ):
        return True

    if (
        isinstance(verification, verificationModule.Between)
        and verification.wanted_from == 0
    ):
        return True

    return False


class StubbedInvocation(MatchingInvocation):
    """
    Denotes the function or method signature after `when` or `expect` is
    called, -- the second part of the fluent interface.

    I.e.    when(obj).method(arg1, ...).thenReturn(value1)
          expect(obj).method(arg1, ...).thenReturn(value1)
                      ^^^^^^^^^^^^^^^^^  StubbedInvocation denotes this part

    The constructor takes the mock object, which is the registered `Mock` for
    the `obj` in the previous examples, and the method name (in the example:
    `method`).

    The `verification` argument is only given when `expect` is being used.
    `strict` is used to overrule the `strict` flag of the `mock` object.

    In the immediately following `__call__` call, the arguments (`args1, ...`)
    are captured.  The third part of the fluent interface (`AnswerSelector`)
    is returned.

    Both calls, `__init__` plus `__call__`, encapsulate a method or function
    call.  But the `__call__` is essentially virtual and can contain
    placeholders and matchers.

    The actual stubbing occurs directly in the `__call__` method.  The stubbing
    is delegated to the `mock` object.  In essence, it will likely patch or add
    a replacement callable to `obj`, i.e.
    `setattr(obj, method_name, new_method)`.

    Note about the nomenclature:  In strict OOP languages, we only had
    "methods", but in Python `obj` could be a class, instance, or module --
    generally speaking: a "callable". (I.e. classes are also just callables;
    there is no "new" keyword in Python.)

    """
    def __init__(
        self,
        mock: Mock,
        method_name: str,
        verification: verificationModule.VerificationMode | None = None,
        strict: bool | None = None
    ) -> None:
        super(StubbedInvocation, self).__init__(mock, method_name)

        #: Holds the verification set up via `expect`.
        #: The verification will be verified implicitly, while using this stub.
        self.verification = verification

        if strict is not None:
            self.strict = strict

        self.answers = CompositeAnswer()

        #: Counts how many times this stub has been 'used'.
        #: A stub gets used, when a real invocation matches its argument
        #: signature, and asks for an answer.
        self.used = 0

        #: Set if `verifyStubbedInvocationsAreUsed` should pass, regardless
        #: of any factual invocation. E.g. set by `expect(..., times=0)`
        self.allow_zero_invocations: bool = \
            verification_has_lower_bound_of_zero(verification)

    def ensure_mocked_object_has_method(self, method_name: str) -> None:
        if not self.mock.has_method(method_name):
            raise InvocationError(
                "You tried to stub a method '%s' the object (%s) doesn't "
                "have." % (method_name, self.mock.mocked_obj))

    def ensure_signature_matches(
        self, method_name: str, args: tuple, kwargs: dict
    ) -> None:
        sig = self.mock.get_signature(method_name)
        if not sig:
            return

        signature.match_signature_allowing_placeholders(sig, args, kwargs)

    def __call__(self, *params: Any, **named_params: Any) -> AnswerSelector:
        if self.strict:
            self.ensure_mocked_object_has_method(self.method_name)
            self.ensure_signature_matches(
                self.method_name, params, named_params)
        self._remember_params(params, named_params)

        self.mock.stub(self.method_name)
        self.mock.finish_stubbing(self)
        return AnswerSelector(self)

    def forget_self(self) -> None:
        self.mock.forget_stubbed_invocation(self)

    def add_answer(self, answer: Callable) -> None:
        self.answers.add(answer)

    def answer_first(self, *args: Any, **kwargs: Any) -> Any:
        self.used += 1
        return self.answers.answer(*args, **kwargs)

    def should_answer(self, invocation: RememberedInvocation) -> None:
        verification = self.verification
        if not verification:
            return

        # This check runs before `answer_first`. We add '1' because we want
        # to know if the verification passes if this call gets through.
        actual_count = self.used + 1

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
                    "\nWanted between: [%s, %s], actual times: %s"
                    % (verification.wanted_from,
                       verification.wanted_to,
                       actual_count))

        # The way mockito's `verify` works is, that it checks off all 'real',
        # remembered invocations, if they get verified. This is a simple
        # mechanism so that a later `ensureNoUnverifiedInteractions` just has
        # to ensure that all invocations have this flag set to ``True``.
        # For verifications set up via `expect` we want all invocations
        # to get verified 'implicitly', on-the-go, so we set this flag here.
        invocation.verified = True

    def verify(self) -> None:
        if self.verification:
            self.verification.verify(self, self.used)

    def check_used(self) -> None:
        if not self.allow_zero_invocations and self.used < len(self.answers):
            raise verificationModule.VerificationError(
                "\nUnused stub: %s" % self)

class StubbedPropertyAccess(StubbedInvocation):
    def ensure_mocked_object_has_method(self, method_name: str) -> None:
        if self.mock.spec is None:
            return

        try:
            inspect.getattr_static(self.mock.spec, method_name)
        except AttributeError:
            raise InvocationError(
                "You tried to stub an attribute '%s' the object (%s) doesn't "
                "have." % (method_name, self.mock.mocked_obj)
            )

    def ensure_signature_matches(self, method_name, args, kwargs):
        return True

    def __call__(self, *params, **named_params):
        if self.strict:
            self.ensure_mocked_object_has_method(self.method_name)
            self.ensure_signature_matches(
                self.method_name, params, named_params)
        self._remember_params(params, named_params)

        self.mock.stub_property(self.method_name)
        self.mock.finish_stubbing(self)
        return AnswerSelector(self)



def return_(value: T) -> Callable[..., T]:
    def answer(*args, **kwargs) -> T:
        return value
    return answer

def raise_(exception: Exception | type[Exception]) -> Callable[..., NoReturn]:
    def answer(*args, **kwargs) -> NoReturn:
        raise exception
    return answer

def discard_self(function: Callable[..., T]) -> Callable[..., T]:
    def function_without_self(*args, **kwargs) -> T:
        args = args[1:]
        return function(*args, **kwargs)
    return function_without_self


class AnswerSelector(object):
    def __init__(self, invocation: StubbedInvocation) -> None:
        self.invocation = invocation
        self.discard_first_arg = \
            invocation.mock.eat_self(invocation.method_name)

    def thenReturn(self, *return_values: Any) -> Self:
        for return_value in return_values or (None,):
            answer = return_(return_value)
            self.__then(answer)
        return self

    def thenRaise(self, *exceptions: Exception | type[Exception]) -> Self:
        for exception in exceptions or (Exception,):
            answer = raise_(exception)
            self.__then(answer)
        return self

    def thenAnswer(self, *callables: Callable) -> Self:
        for callable in callables or (return_(None),):
            answer = callable
            if self.discard_first_arg:
                answer = discard_self(answer)
            self.__then(answer)
        return self

    def thenCallOriginalImplementation(self) -> Self:
        answer = self.invocation.mock.get_original_method(
            self.invocation.method_name
        )
        if isinstance(self.invocation, StubbedPropertyAccess):
            if not hasattr(answer, '__get__'):
                raise AnswerError(
                    "'%s' has no original implementation for '%s'." %
                    (
                        self.invocation.mock.mocked_obj,
                        self.invocation.method_name,
                    )
                )
            self.__then(self._property_descriptor_answer(answer))
            return self

        if answer is None:
            raise AnswerError(
                "'%s' has no original implementation for '%s'." %
                (self.invocation.mock.mocked_obj, self.invocation.method_name)
            )

        if (
            # A classmethod is not callable
            # and a staticmethod is not callable in old version of python,
            # so we get the underlying function.
            isinstance(answer, classmethod) or isinstance(answer, staticmethod)
            # If the method is bound, we unbind it.
            or inspect.ismethod(answer)
        ):
            answer = answer.__func__

        self.__then(answer)
        return self

    def _property_descriptor_answer(self, descriptor: object) -> Callable:
        def answer(*args: Any, **kwargs: Any) -> Any:
            obj, type_ = self.invocation.mock.get_current_property_access(
                self.invocation.method_name
            )
            return descriptor.__get__(obj, type_)

        return answer

    def __then(self, answer: Callable) -> None:
        self.invocation.add_answer(answer)

    def __enter__(self) -> None:
        pass

    def __exit__(self, *exc_info) -> None:
        self.invocation.verify()
        if os.environ.get("MOCKITO_CONTEXT_MANAGERS_CHECK_USAGE", "1") == "1":
            self.invocation.check_used()
        self.invocation.forget_self()


class CompositeAnswer(object):
    def __init__(self) -> None:
        #: Container for answers, which are just ordinary callables
        self.answers: deque[Callable] = deque()

        #: Counter for the maximum answers we ever had
        self.answer_count = 0

    def __len__(self) -> int:
        # The minimum is '1' bc we always have a default answer of 'None'
        return max(1, self.answer_count)

    def add(self, answer: Callable) -> None:
        self.answer_count += 1
        self.answers.append(answer)

    def answer(self, *args: Any, **kwargs: Any) -> Any:
        if len(self.answers) == 0:
            return None

        if len(self.answers) == 1:
            a = self.answers[0]
        else:
            a = self.answers.popleft()

        return a(*args, **kwargs)

