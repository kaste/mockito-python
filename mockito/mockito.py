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

from . import verification
from .mocking import mock, TestDouble
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


def verify(obj, times=1, atleast=None, atmost=None, between=None,
           inorder=False):

    if isinstance(obj, TestDouble):
        mocked_object = obj
    else:
        mocked_object = mock_registry.mock_for(obj)

    verification_fn = _get_wanted_verification(
        times=times, atleast=atleast, atmost=atmost, between=between)
    if inorder:
        verification_fn = verification.InOrder(verification_fn)

    mocked_object.expect_verifying(verification_fn)
    return mocked_object


def when(obj, strict=True):
    if isinstance(obj, mock):
        theMock = obj
    else:
        theMock = mock_registry.mock_for(obj)
        if theMock is None:
            theMock = mock(obj, strict=strict)
            # If we call when on something that is not TestDouble that means
            # we're trying to stub real object, (class, module etc.). Not to
            # be confused with generating stubs from real classes.
            theMock.stubbing_real_object = True

    theMock.expect_stubbing()
    return theMock

def expect(obj, strict=True,
           times=None, atleast=None, atmost=None, between=None):
    verification_fn = _get_wanted_verification(
        times=times, atleast=atleast, atmost=atmost, between=between)

    mock = when(obj, strict=strict)
    mock.expect_stubbing(verification_fn)
    return mock



def unstub():
    """Unstubs all stubbed methods and functions"""
    mock_registry.unstub_all()


def verifyNoMoreInteractions(*objs):
    for obj in objs:
        if isinstance(obj, mock):
            theMock = obj
        else:
            theMock = mock_registry.mock_for(obj)

        for i in theMock.stubbed_invocations:
            i.verify()

        for i in theMock.invocations:
            if not i.verified:
                raise VerificationError("\nUnwanted interaction: " + str(i))


def verifyZeroInteractions(*mocks):
    verifyNoMoreInteractions(*mocks)
