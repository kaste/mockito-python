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

import operator

from . import invocation
from . import verification

from .utils import deprecated, get_obj, get_obj_attr_tuple
from .mocking import Mock
from .mock_registry import mock_registry
from .verification import VerificationError


class ArgumentError(Exception):
    pass


__tracebackhide__ = operator.methodcaller(
    "errisinstance", (ArgumentError, VerificationError)
)


def _invalid_between(between):
    if between is not None:
        try:
            if len(between) == 1:
                start, end = between[0], float('inf')
            else:
                start, end = between
            if start < 0 or start > end:
                return True
        except Exception:
            return True
    return False


def _get_wanted_verification(
        times=None, atleast=None, atmost=None, between=None):
    if (times, atleast, atmost, between).count(None) < 3:
        raise ArgumentError(
            "You can set only one of the arguments: 'times', 'atleast', "
            "'atmost' or 'between'.")

    if times is not None:
        if times < 0:
            raise ArgumentError(
                "'times' argument has invalid value.\n"
                f"It should be at least 0.  You wanted to set it to: {times}"
            )
        return verification.Times(times)
    if atleast is not None:
        if atleast < 1:
            raise ArgumentError(
                "'atleast' argument has invalid value.\n"
                f"It should be at least 1.  You wanted to set it to: {atleast}"
            )
        return verification.AtLeast(atleast)
    if atmost is not None:
        if atmost < 1:
            raise ArgumentError(
                "'atmost' argument has invalid value.\n"
                f"It should be at least 1.  You wanted to set it to: {atmost}"
            )
        return verification.AtMost(atmost)
    if between is not None:
        if _invalid_between(between):
            raise ArgumentError(
                "'between' argument has invalid value.\n"
                "It should consist of positive values with second number "
                "greater than first e.g. (1, 4) or (0, 3) or (2, 2), "
                "or a single non-negative number for open-ended range "
                f"e.g. (0,).  You wanted to set it to: {between}"
            )
        return verification.Between(*between)
    return None


def _get_mock(obj, strict=True):
    theMock = mock_registry.mock_for(obj)
    if theMock is None:
        theMock = Mock(obj, strict=strict, spec=obj)
        mock_registry.register(obj, theMock)
    return theMock

def _get_mock_or_raise(obj):
    theMock = mock_registry.mock_for(obj)
    if theMock is None:
        raise ArgumentError("obj '%s' is not registered" % obj)
    return theMock

def verify(obj, times=None, atleast=None, atmost=None, between=None,
           inorder=False):
    """Central interface to verify interactions.

    `verify` uses a fluent interface::

        verify(<obj>, times=2).<method_name>(<args>)

    `args` can be as concrete as necessary. Often a catch-all is enough,
    especially if you're working with strict mocks, bc they throw at call
    time on unwanted, unconfigured arguments::

        from mockito import ANY, ARGS, KWARGS
        when(manager).add_tasks(1, 2, 3)
        ...
        # no need to duplicate the specification; every other argument pattern
        # would have raised anyway.
        verify(manager).add_tasks(1, 2, 3)  # duplicates `when`call
        verify(manager).add_tasks(*ARGS)
        verify(manager).add_tasks(...)       # Py3
        verify(manager).add_tasks(Ellipsis)  # Py2

    """

    if isinstance(obj, str):
        obj = get_obj(obj)

    verification_fn = (
        _get_wanted_verification(
            times=times, atleast=atleast, atmost=atmost, between=between
        ) or verification.Times(1)
    )
    if inorder:
        verification_fn = verification.InOrder(verification_fn)

    theMock = _get_mock_or_raise(obj)

    class Verify(object):
        def __getattr__(self, method_name):
            return invocation.VerifiableInvocation(
                theMock, method_name, verification_fn)

    return Verify()


class _OMITTED(object):
    def __repr__(self):
        return 'OMITTED'


OMITTED = _OMITTED()


def when(obj, strict=True):
    """Central interface to stub functions on a given `obj`

    `obj` should be a module, a class or an instance of a class; it can be
    a Dummy you created with :func:`mock`. ``when`` exposes a fluent interface
    where you configure a stub in three steps::

        when(<obj>).<method_name>(<args>).thenReturn(<value>)

    Compared to simple *patching*, stubbing in mockito requires you to specify
    concrete `args` for which the stub will answer with a concrete `<value>`.
    All invocations that do not match this specific call signature will be
    rejected. They usually throw at call time.

    Stubbing in mockito's sense thus means not only to get rid of unwanted
    side effects, but effectively to turn function calls into constants.

    E.g.::

        # Given ``dog`` is an instance of a ``Dog``
        when(dog).bark('Grrr').thenReturn('Wuff')
        when(dog).bark('Miau').thenRaise(TypeError())

        # With this configuration set up:
        assert dog.bark('Grrr') == 'Wuff'
        dog.bark('Miau')  # will throw TypeError
        dog.bark('Wuff')  # will throw unwanted interaction

    Stubbing can effectively be used as monkeypatching; usage shown with
    the `with` context managing::

        with when(os.path).exists('/foo').thenReturn(True):
            ...

    Most of the time verifying your interactions is not necessary, because
    your code under tests implicitly verifies the return value by evaluating
    it. See :func:`verify` if you need to, see also :func:`expect` to setup
    expected call counts up front.

    If your function is pure side effect and does not return something, you
    can omit the specific answer. The function will then return `None` as by
    default for Python functions::

        when(manager).do_work().thenReturn()
        # However, using `expect` may read better.
        expect(manager).do_work()

    `when` verifies the method name, the expected argument signature, and the
    actual, factual arguments your code under test uses against the original
    object and its function so its easier to spot changing interfaces.

    Sometimes it's tedious to spell out all arguments::

        from mockito import ANY, ARGS, KWARGS
        when(requests).get('http://example.com/', **KWARGS).thenReturn(...)
        when(os.path).exists(ANY)
        when(os.path).exists(ANY(str))

    .. note:: You must :func:`unstub` after stubbing, or use `with`
        statement.

    Set ``strict=False`` to bypass the function signature checks.

    See related :func:`when2` which has a more pythonic interface.

    """

    if isinstance(obj, str):
        obj = get_obj(obj)

    theMock = _get_mock(obj, strict=strict)

    class When(object):
        def __getattr__(self, method_name):
            return invocation.StubbedInvocation(
                theMock, method_name, strict=strict)

    return When()


def when2(fn, *args, **kwargs):
    """Stub a function call with the given arguments

    Exposes a more pythonic interface than :func:`when`. See :func:`when` for
    more documentation.

    Returns `AnswerSelector` interface which exposes `thenReturn`,
    `thenRaise`, `thenAnswer`, and `thenCallOriginalImplementation` as usual.
    Always `strict`.

    Usage::

        # Given `dog` is an instance of a `Dog`
        when2(dog.bark, 'Miau').thenReturn('Wuff')

    .. note:: You must :func:`unstub` after stubbing, or use `with`
        statement.

    """
    obj, name = get_obj_attr_tuple(fn)
    theMock = _get_mock(obj, strict=True)
    return invocation.StubbedInvocation(theMock, name)(*args, **kwargs)


def patch(fn, attr_or_replacement, replacement=None):
    """Patch/Replace a function.

    This is really like monkeypatching, but *note* that all interactions
    will be recorded and can be verified. That is, using `patch` you stay in
    the domain of mockito.

    Two ways to call this. Either::

        patch(os.path.exists, lambda str: True)  # two arguments
        # OR
        patch(os.path, 'exists', lambda str: True)  # three arguments

    If called with three arguments, the mode is *not* strict to allow *adding*
    methods. If called with two arguments, mode is always `strict`.

    .. note:: You must :func:`unstub` after stubbing, or use `with`
        statement.

    """
    if replacement is None:
        replacement = attr_or_replacement
        return when2(fn, Ellipsis).thenAnswer(replacement)
    else:
        obj, name = fn, attr_or_replacement
        theMock = _get_mock(obj, strict=True)
        return invocation.StubbedInvocation(
            theMock, name, strict=False)(Ellipsis).thenAnswer(replacement)



def expect(obj, strict=True,
           times=None, atleast=None, atmost=None, between=None):
    """Stub a function call, and set up an expected call count.

    Usage::

        # Given `dog` is an instance of a `Dog`
        expect(dog, times=1).bark('Wuff').thenReturn('Miau')
        dog.bark('Wuff')
        dog.bark('Wuff')  # will throw at call time: too many invocations

        # maybe if you need to ensure that `dog.bark()` was called at all
        verifyExpectedInteractions()

    .. note:: You must :func:`unstub` after stubbing, or use `with`
        statement.

    See :func:`when`, :func:`when2`, :func:`verifyExpectedInteractions`

    """

    if isinstance(obj, str):
        obj = get_obj(obj)

    theMock = _get_mock(obj, strict=strict)

    verification_fn = _get_wanted_verification(
        times=times, atleast=atleast, atmost=atmost, between=between)

    class Expect(object):
        def __getattr__(self, method_name):
            return invocation.StubbedInvocation(
                theMock, method_name, verification=verification_fn,
                strict=strict)

    return Expect()



def unstub(*objs):
    """Unstubs all stubbed methods and functions

    If you don't pass in any argument, *all* registered mocks and
    patched modules, classes etc. will be unstubbed.

    Note that additionally, the underlying registry will be cleaned.
    After an `unstub` you can't :func:`verify` anymore because all
    interactions will be forgotten.
    """

    if objs:
        for obj in objs:
            mock_registry.unstub(obj)
    else:
        mock_registry.unstub_all()


def forget_invocations(*objs):
    """Forget all invocations of given objs.

    If you already *call* mocks during your setup routine, you can now call
    ``forget_invocations`` at the end of your setup, and have a clean
    'recording' for your actual test code. T.i. you don't have
    to count the invocations from your setup code anymore when using
    :func:`verify` afterwards.
    """
    for obj in objs:
        theMock = _get_mock_or_raise(obj)
        theMock.clear_invocations()


def ensureNoUnverifiedInteractions(*objs):
    """Check if any given object has any unverified interaction.

    You can use this after `verify`-ing to ensure no other interactions
    happened.

    Can lead to over-specified tests.
    """
    verifyExpectedInteractions(*objs)

    for obj in objs:
        theMock = _get_mock_or_raise(obj)

        for i in theMock.invocations:
            if not i.verified:
                raise VerificationError("\nUnwanted interaction: %s" % i)


def verifyZeroInteractions(*objs):
    """Verify that no methods have been called on given objs.

    Rarely used because `verify(..., times=0)` is more explicit.  Also:
    strict mocks usually throw early on unexpected, unstubbed invocations.
    For them, there may be no need to verify afterwards.
    `expect(..., times=0)` may also appropriate.

    Partial mocks ('monkeypatched' objects or modules) only look at the
    stubbed invocations as the actual usage gets recorded only for them.
    However, you could use `spy` and inject it.

    """
    for obj in objs:
        theMock = _get_mock_or_raise(obj)

        if len(theMock.invocations) > 0:
            raise VerificationError(
                "\nUnwanted interaction: %s" % theMock.invocations[0])



def verifyExpectedInteractions(*objs):
    """Verifies that expectations set via `expect` are met

    E.g.::

        expect(os.path, times=1).exists(...).thenReturn(True)
        os.path('/foo')
        verifyExpectedInteractions(os.path)  # ok, called once

    If you leave out the argument *all* registered objects will
    be checked.

    .. note:: **DANGERZONE**: If you did not :func:`unstub` correctly,
        it is possible that old registered mocks, from other tests
        leak.

    See related :func:`expect`
    """

    if objs:
        theMocks = map(_get_mock_or_raise, objs)
    else:
        theMocks = mock_registry.get_registered_mocks()

    for mock in theMocks:
        for i in mock.stubbed_invocations:
            i.verify()


def verifyStubbedInvocationsAreUsed(*objs):
    """Ensure stubs are actually used.

    This functions just ensures that stubbed methods are actually used. Its
    purpose is to detect interface changes after refactorings. It is meant
    to be invoked usually without arguments just before :func:`unstub`.

    """
    if objs:
        theMocks = map(_get_mock_or_raise, objs)
    else:
        theMocks = mock_registry.get_registered_mocks()


    for mock in theMocks:
        for i in mock.stubbed_invocations:
            i.check_used()


@deprecated(
    "'verifyNoMoreInteractions' is deprecated. "
    "Use 'ensureNoUnverifiedInteractions' instead."
)
def verifyNoMoreInteractions(*objs):
    return ensureNoUnverifiedInteractions(*objs)

verifyNoMoreInteractions.__doc__ = (        # noqa: E305
    ensureNoUnverifiedInteractions.__doc__  # type: ignore[operator]
    + "\n\nDeprecated: Use 'ensureNoUnverifiedInteractions' instead."
)


@deprecated(
    "'verifyNoUnwantedInteractions' is deprecated. "
    "Use 'verifyExpectedInteractions' instead."
)
def verifyNoUnwantedInteractions(*args, **kwargs):
    return verifyExpectedInteractions(*args, **kwargs)

verifyNoUnwantedInteractions.__doc__ = (  # noqa: E305
    verifyExpectedInteractions.__doc__    # type: ignore[operator]
    + "\n\nDeprecated: Use 'verifyExpectedInteractions' instead."
)
