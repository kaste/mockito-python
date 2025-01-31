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

import operator
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .invocation import MatchingInvocation

__all__ = ['never', 'VerificationError']


class VerificationError(AssertionError):
    '''Indicates error during verification of invocations.

    Raised if verification fails. Error message contains the cause.
    '''
    pass


__tracebackhide__ = operator.methodcaller("errisinstance", VerificationError)


class VerificationMode(ABC):
    @abstractmethod
    def verify(
        self, invocation: MatchingInvocation, actual_count: int
    ) -> None:
        pass


class AtLeast(VerificationMode):
    def __init__(self, wanted_count: int) -> None:
        self.wanted_count = wanted_count

    def verify(
        self, invocation: MatchingInvocation, actual_count: int
    ) -> None:
        if actual_count == 0:
            msg = error_message_for_unmatched_invocation(invocation)
            raise VerificationError(msg)

        if actual_count < self.wanted_count:
            raise VerificationError("\nWanted at least: %i, actual times: %i"
                                    % (self.wanted_count, actual_count))

    def __repr__(self):
        return "<%s wanted=%s>" % (type(self).__name__, self.wanted_count)

class AtMost(VerificationMode):
    def __init__(self, wanted_count: int) -> None:
        self.wanted_count = wanted_count

    def verify(
        self, invocation: MatchingInvocation, actual_count: int
    ) -> None:
        if actual_count > self.wanted_count:
            raise VerificationError("\nWanted at most: %i, actual times: %i"
                                    % (self.wanted_count, actual_count))

    def __repr__(self):
        return "<%s wanted=%s>" % (type(self).__name__, self.wanted_count)

class Between(VerificationMode):
    def __init__(
        self, wanted_from: int, wanted_to: int | float = float('inf')
    ) -> None:
        self.wanted_from = wanted_from
        self.wanted_to = wanted_to

    def verify(
        self, invocation: MatchingInvocation, actual_count: int
    ) -> None:
        if actual_count < self.wanted_from or actual_count > self.wanted_to:
            raise VerificationError(
                "\nWanted between: [%s, %s], actual times: %s"
                % (self.wanted_from, self.wanted_to, actual_count))

    def __repr__(self):
        return "<Between [%s, %s]>" % (self.wanted_from, self.wanted_to)

class Times(VerificationMode):
    def __init__(self, wanted_count: int) -> None:
        self.wanted_count = wanted_count

    def verify(
        self, invocation: MatchingInvocation, actual_count: int
    ) -> None:
        if actual_count == self.wanted_count:
            return

        if actual_count == 0:
            msg = error_message_for_unmatched_invocation(invocation)
            raise VerificationError(msg)

        if self.wanted_count == 0:
            raise VerificationError(
                "\nUnwanted invocation of %s, times: %i"
                % (invocation, actual_count))
        else:
            raise VerificationError("\nWanted times: %i, actual times: %i"
                                    % (self.wanted_count, actual_count))

    def __repr__(self):
        return "<%s wanted=%s>" % (type(self).__name__, self.wanted_count)


def error_message_for_unmatched_invocation(
    invocation: MatchingInvocation
) -> str:
    invocations = (
        [
            invoc
            for invoc in invocation.mock.invocations
            if invoc.method_name == invocation.method_name
        ]
        or invocation.mock.invocations
    )
    wanted_section = (
        "\nWanted but not invoked:\n\n    %s\n" % invocation
    )
    instead_section = (
        "\nInstead got:\n\n    %s\n"
        % "\n    ".join(map(str, invocations))
    ) if invocations else ""

    return "%s%s\n" % (wanted_section, instead_section)


class InOrder(VerificationMode):
    '''Verifies invocations in order.

    Verifies if invocation was in expected order, and if yes -- degrades to
    original Verifier (AtLeast, Times, Between, ...).
    '''

    def __init__(self, original_verification: VerificationMode) -> None:
        '''

        @param original_verification: Original verification to degrade to if
                                      order of invocation was ok.
        '''
        self.original_verification = original_verification

    def verify(
        self, wanted_invocation: MatchingInvocation, count: int
    ) -> None:
        for invocation in wanted_invocation.mock.invocations:
            if not invocation.verified_inorder:
                if not wanted_invocation.matches(invocation):
                    raise VerificationError(
                        '\nWanted %s to be invoked,'
                        '\ngot    %s instead.' %
                        (wanted_invocation, invocation))
                invocation.verified_inorder = True
                break
        # proceed with original verification
        self.original_verification.verify(wanted_invocation, count)


never = 0
