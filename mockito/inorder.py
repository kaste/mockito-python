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

    def __init__(self, *objects: object):
        counter = Counter(objects)
        duplicates = [d for d, freq in counter.items() if freq > 1]
        if duplicates:
            raise ValueError(
                f"\nThe following Mocks are duplicated: "
                f"{[str(d) for d in duplicates]}"
            )
        self._objects = objects
        for obj in objects:
            if m := mock_registry.mock_for(obj):
                m.attach(self)

        self.ordered_invocations: Deque[RealInvocation] = deque()

    def update(self, invocation: RealInvocation) -> None:
        self.ordered_invocations.append(invocation)

    def verify(self, obj: object):
        """
        Central method of InOrder class.
        Use this method to verify the calling order of observed mocks.
        :param obj: obj to verify the ordered invocation

        """
        expected_mock = mock_registry.mock_for(obj)
        if expected_mock is None:
            raise VerificationError(
                f"\n{obj} is not setup with any stubbings or expectations."
            )

        if obj not in self._objects:
            raise VerificationError(
                f"\n{obj} is not part of that InOrder."
            )

        if not self.ordered_invocations:
            raise VerificationError(
                "\nThere are no recorded invocations."
            )

        # Find the next invocation in global order that hasn't been used
        # for "in-order" verification yet.
        next_invocation = next(
            (inv for inv in self.ordered_invocations if not inv.verified_inorder),
            None,
        )
        if next_invocation is None:
            raise VerificationError(
                "\nThere are no more recorded invocations."
            )

        called_mock = next_invocation.mock
        if called_mock != expected_mock:
            called_obj = mock_registry.obj_for(called_mock)
            if called_obj is None:
                raise RuntimeError(
                    f"{called_mock} is not in the registry (anymore)."
                )
            raise VerificationError(
                f"\nWanted a call from {obj}, but "
                f"got {called_obj}.{next_invocation} instead!"
            )
        return verify_main(obj=obj, atleast=1, inorder=True)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for obj in self._objects:
            if m := mock_registry.mock_for(obj):
                m.detach(self)
