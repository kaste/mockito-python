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

from collections import Counter, deque
from typing import Tuple, Deque

from .verification import VerificationError
from .invocation import RealInvocation
from .mocking import Mock
from .mockito import verify as verify_main
from .mock_registry import mock_registry


def verify(object, *args, **kwargs):
    kwargs['inorder'] = True
    return verify_main(object, *args, **kwargs)


class InOrder:

    def __init__(self, *mocks: Mock):
        counter = Counter(mocks)
        duplicates = [d for d, freq in counter.items() if freq > 1]
        if duplicates:
            raise ValueError(
                f"\nThe following Mocks are duplicated: "
                f"{[str(d) for d in duplicates]}"
            )
        self._mocks = mocks
        for mock in mocks:
            m = mock_registry.mock_for(mock)
            if m:
                m.attach(self)

        self.ordered_invocations: Deque[RealInvocation] = deque()

    def update(self, invocation: RealInvocation) -> None:
        self.ordered_invocations.append(invocation)

    def verify(self, mock):
        """
        Central method of InOrder class.
        Use this method to verify the calling order of observed mocks.
        :param mock: mock to verify the ordered invocation

        """

        if mock not in self._mocks:
            raise VerificationError(
                f"\nUnexpected call from not observed {mock}."
            )

        if not self.ordered_invocations:
            raise VerificationError(
                f"\nTrying to verify ordered invocation of {mock}, "
                f"but no other invocations have been recorded."
            )
        invocation = self.ordered_invocations.popleft()
        called_mock = invocation.mock
        # Basically we need a reverse map here.
        # `mock_for` is a find_mock_for_obj and we do a find_obj_for_mock
        obj = next(o for o, m in mock_registry.mocks._store if m == called_mock)

        expected_mock = mock_registry.mock_for(mock)
        if called_mock != expected_mock:
            raise VerificationError(
                f"\nWanted a call from {mock}, but "
                f"got {invocation} from {obj} instead!"
            )
        return verify_main(obj=mock, atleast=1, inorder=True)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for mock in self._mocks:
            mock.detach(self)
