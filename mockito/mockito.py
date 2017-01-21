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

    Stubbing in mockito's sense means turning functions into constants.
    You specify more or less concrete arguments and a constant output, a return
    value or a raised exception, for it. You hereby set expected interactions.
    All interactions that do not met these expectations, the specified
    arguments, will be rejected. They throw immediately at call time.

    E.g.::

        when(dog).bark('Grrr').thenReturn('Wuff')
        when(dog).bark('Miau').thenRaise(TypeError())
        assert dog.bark('Grrr') == 'Wuff'
        verify(dog).bark('Grrr')

        dog.bark('Miau')  # will throw TypeError
        dog.bark('Wuff')  # will throw unwanted interaction

    Stubbing can effectively be used as monkeypatching; usage shown with
    the ``with`` context managing::

        with when(os.path).exists('/foo').thenReturn(True):
            ...

    Most of the time verifying your interactions is not necessary, because
    your code under tests implicitly verifies the return value by evaluating
    it.

    If your function is pure side effect and does not return something, you
    can omit the specific answer. Python's default here is ``None``::

        when(manager).do_work()

    ``when`` verifies the method name, the expected argument signature, and the
    actual, factual arguments your code under test uses against the original
    object and its function so its easier to spot changing interfaces.

    Sometimes it's tedious to spell out all arguments::

        from mockito import ANY, ARGS, KWARGS
        when(requests).get('http://example.com/', **KWARGS).thenReturn(...)
        when(os.path).exists(ANY)
        when(os.path).exists(ANY(str))

    This is especially handy for subsequent ``verify`` calls::

        when(manager).add_tasks(1, 2, 3)
        ...
        # no need to duplicate the specification; every other argument pattern
        # would have raised anyway.
        verify(manager).add_tasks(*ARGS)
        verify(manager).add_tasks(...)       # Py3
        verify(manager).add_tasks(Ellipsis)  # Py2


    """
    theMock = _get_mock(obj, strict=strict)

    class When(object):
        def __getattr__(self, method_name):
            return invocation.StubbedInvocation(theMock, method_name)

    return When()


def when2(fn, *args, **kwargs):
    """Specialized ``when`` that takes a function and potential arguments

    Returns ``AnswerSelector`` interface which exposes ``thenReturn``,
    ``thenRaise``, and ``thenAnswer`` as usual. Always ``strict``.

    Usage::

        # when(dog).bark('Miau').thenReturn('Wuff')
        when2(dog.bark, 'Miau').thenReturn('Wuff')



    """
    obj, name, fn = get_function_host(fn)
    theMock = Mock(obj, strict=True, spec=obj)
    mock_registry.register(obj, theMock)
    return invocation.StubbedInvocation(theMock, name)(*args, **kwargs)


def patch(fn, new_fn):
    when2(fn, Ellipsis).thenAnswer(new_fn)


def expect(obj, strict=True,
           times=None, atleast=None, atmost=None, between=None):

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
