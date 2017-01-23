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

from . import invocation
from . import verification

from .utils import get_function_host
from .mocking import Mock
from .mock_registry import mock_registry
from .verification import VerificationError


class ArgumentError(Exception):
    pass


def _multiple_arguments_in_use(*args):
    return len(filter(lambda x: x, args)) > 1


def _invalid_argument(value):
    return (value is not None and value < 1) or value == 0


def _invalid_between(between):
    if between is not None:
        start, end = between
        if start > end or start < 0:
            return True
    return False

def _get_wanted_verification(
        times=None, atleast=None, atmost=None, between=None):
    if times is not None and times < 0:
        raise ArgumentError("'times' argument has invalid value.\n"
                            "It should be at least 0. You wanted to set it to:"
                            " %i" % times)
    if _multiple_arguments_in_use(atleast, atmost, between):
        raise ArgumentError(
            "You can set only one of the arguments: 'atleast', "
            "'atmost' or 'between'.""")
    if _invalid_argument(atleast):
        raise ArgumentError("'atleast' argument has invalid value.\n"
                            "It should be at least 1.  You wanted to set it "
                            "to: %i" % atleast)
    if _invalid_argument(atmost):
        raise ArgumentError("'atmost' argument has invalid value.\n"
                            "It should be at least 1.  You wanted to set it "
                            "to: %i""" % atmost)
    if _invalid_between(between):
        raise ArgumentError("""'between' argument has invalid value.
            It should consist of positive values with second number not greater
            than first e.g. [1, 4] or [0, 3] or [2, 2]
            You wanted to set it to: %s""" % between)

    if atleast:
        return verification.AtLeast(atleast)
    elif atmost:
        return verification.AtMost(atmost)
    elif between:
        return verification.Between(*between)
    elif times is not None:
        return verification.Times(times)

def _get_mock(obj, strict=True):
    theMock = mock_registry.mock_for(obj)
    if theMock is None:
        theMock = Mock(obj, strict=strict, spec=obj)
        mock_registry.register(obj, theMock)
    return theMock

def verify(obj, times=1, atleast=None, atmost=None, between=None,
           inorder=False):
    """Central interface to verify interactions.

    ``verify`` uses a fluent interface::

        verify(<obj>, times=2).<method_name>(<args>)

    `args` can be as concrete as neccessary. Often a catch-all is enough,
    especially if you're working with strict mocks, bc they throw at call
    time on unwanted, unconfigured arguments::

        from mockito import ANY, ARGS, KWARGS
        when(manager).add_tasks(1, 2, 3)
        ...
        # no need to duplicate the specification; every other argument pattern
        # would have raised anyway.
        verify(manager).add_tasks(*ARGS)
        verify(manager).add_tasks(...)       # Py3
        verify(manager).add_tasks(Ellipsis)  # Py2

    """

    verification_fn = _get_wanted_verification(
        times=times, atleast=atleast, atmost=atmost, between=between)
    if inorder:
        verification_fn = verification.InOrder(verification_fn)

    # FIXME?: Catch error if obj is neither a Mock nor a known stubbed obj
    theMock = _get_mock(obj)

    class Verify(object):
        def __getattr__(self, method_name):
            return invocation.VerifiableInvocation(
                theMock, method_name, verification_fn)

    return Verify()


def when(obj, strict=True):
    """Central interface to stub functions on a given ``obj``

    ``obj`` should be a module, a class or an instance of a class; it can be
    a Dummy you created with ``mock``. ``when`` exposes a fluent interface
    where you configure a stub in three steps::

        when(<obj>).<method_name>(<args>).thenReturn(<value>)

    Compared to simple *patching*, stubbing in mockito requires you to specify
    conrete ``args`` for which the stub will answer with a concrete
    ``<value>``. All invocations that do not match this specific call signature
    will be rejected. They usually throw at call time.

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
    the ``with`` context managing::

        with when(os.path).exists('/foo').thenReturn(True):
            ...

    Most of the time verifying your interactions is not necessary, because
    your code under tests implicitly verifies the return value by evaluating
    it. See ``verify`` if you need to, see also ``expect`` to setup expected
    call counts up front.

    If your function is pure side effect and does not return something, you
    can omit the specific answer. The default then is ``None``::

        when(manager).do_work()

    ``when`` verifies the method name, the expected argument signature, and the
    actual, factual arguments your code under test uses against the original
    object and its function so its easier to spot changing interfaces.

    Sometimes it's tedious to spell out all arguments::

        from mockito import ANY, ARGS, KWARGS
        when(requests).get('http://example.com/', **KWARGS).thenReturn(...)
        when(os.path).exists(ANY)
        when(os.path).exists(ANY(str))

    **MUST ``unstub`` after stubbing.** Or use ``with`` statement.

    Set ``strict=False`` to bypass the function signature checks.

    See related ``when2`` which has a more pythonic interface.

    """
    theMock = _get_mock(obj, strict=strict)

    class When(object):
        def __getattr__(self, method_name):
            return invocation.StubbedInvocation(theMock, method_name)

    return When()


def when2(fn, *args, **kwargs):
    """Stub a function call with the given arguments

    Exposes a more pythonic interface than ``when``. See ``when`` for more
    documentation.

    Returns ``AnswerSelector`` interface which exposes ``thenReturn``,
    ``thenRaise``, and ``thenAnswer`` as usual. Always ``strict``.

    Usage::

        # Given ``dog`` is an instance of a ``Dog``
        when2(dog.bark, 'Miau').thenReturn('Wuff')

    **MUST ``unstub`` after stubbing.** Or use ``with`` statement.

    """
    obj, name, fn = get_function_host(fn)
    theMock = Mock(obj, strict=True, spec=obj)
    mock_registry.register(obj, theMock)
    return invocation.StubbedInvocation(theMock, name)(*args, **kwargs)


def patch(fn, new_fn):
    when2(fn, Ellipsis).thenAnswer(new_fn)


def expect(obj, strict=True,
           times=None, atleast=None, atmost=None, between=None):
    """Stub a function call, and set up an expected call count.

    Usage::

        # Given ``dog`` is an instance of a ``Dog``
        expect(dog, times=1).bark('Wuff').thenReturn('Miau')
        dog.bark('Wuff')
        dog.bark('Wuff')  # will throw at call time: too many invocations

        # maybe if you need to ensure that ``dog.bark()`` was called at all
        verifyNoUnwantedInteractions()

    **MUST ``unstub`` after stubbing.** Or use ``with`` statement.

    See ``when``, ``when2``

    """

    theMock = _get_mock(obj, strict=strict)

    verification_fn = _get_wanted_verification(
        times=times, atleast=atleast, atmost=atmost, between=between)

    class Expect(object):
        def __getattr__(self, method_name):
            return invocation.StubbedInvocation(
                theMock, method_name, verification_fn)

    return Expect()



def unstub(*objs):
    """Unstubs all stubbed methods and functions

    If you don't pass in any argument, *all* registered mocks and
    patched modules, classes etc. will be unstubbed.

    Note that additionally, the underlying registry will be cleaned.
    After an ``unstub`` you can't ``verify`` anymore because all
    interactions will be forgotten.
    """

    if objs:
        for obj in objs:
            mock_registry.unstub(obj)
    else:
        mock_registry.unstub_all()


def verifyNoMoreInteractions(*objs):
    verifyNoUnwantedInteractions(*objs)

    for obj in objs:
        theMock = _get_mock(obj)

        for i in theMock.invocations:
            if not i.verified:
                raise VerificationError("\nUnwanted interaction: " + str(i))


def verifyZeroInteractions(*mocks):
    verifyNoMoreInteractions(*mocks)


def verifyNoUnwantedInteractions(*objs):
    """Verifies that expectations set via ``expect`` are met

    E.g.::

        expect(os.path, times=1).exists(...).thenReturn(True)
        os.path('/foo')
        verifyNoUnwantedInteractions(os.path)  # ok, called once

    If you leave out the argument *all* registered objects will
    be checked. **DANGERZONE**: If you did not ``unstub`` correctly,
    it is possible that old registered mocks, from other tests
    leak.
    """

    if objs:
        theMocks = map(_get_mock, objs)
    else:
        theMocks = mock_registry.get_registered_mocks()

    for mock in theMocks:
        for i in mock.stubbed_invocations:
            i.verify()
