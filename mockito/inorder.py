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

from collections import deque
from functools import partial
from typing import Deque

from .verification import VerificationError
from .invocation import (
    RealInvocation,
    VerifiableInvocation,
    verification_has_lower_bound_of_zero,
)
from .mockito import ArgumentError, verify as verify_main
from .mock_registry import mock_registry


def verify(object, *args, **kwargs):
    kwargs['inorder'] = True
    return verify_main(object, *args, **kwargs)


class InOrder:

    def __init__(self, *objects: object):
        objects_: list[object] = []
        for obj in objects:
            if any(observed is obj for observed in objects_):
                raise ValueError(f"{obj} is provided more than once")
            objects_.append(obj)
        self._objects = objects_
        self._attach_all()
        self.ordered_invocations: Deque[RealInvocation] = deque()

    def _attach_all(self):
        for obj in self._objects:
            if m := mock_registry.mock_for(obj):
                m.attach(self)

    def update(self, invocation: RealInvocation) -> None:
        self.ordered_invocations.append(invocation)

    def verify(
        self,
        obj: object,
        times=None,
        atleast=None,
        atmost=None,
        between=None,
    ):
        """
        Central method of InOrder class.
        Use this method to verify the calling order of observed mocks.
        :param obj: obj to verify the ordered invocation

        """
        expected_mock = mock_registry.mock_for(obj)
        if expected_mock is None:
            raise ArgumentError(
                f"\n{obj} is not setup with any stubbings or expectations."
            )

        if not any(observed is obj for observed in self._objects):
            raise ArgumentError(
                f"\n{obj} is not part of that InOrder."
            )

        return verify_main(
            obj=obj,
            times=times,
            atleast=atleast,
            atmost=atmost,
            between=between,
            _factory=partial(InOrderVerifiableInvocation, inorder=self),
        )

    def __enter__(self):
        self._attach_all()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for obj in self._objects:
            if m := mock_registry.mock_for(obj):
                m.detach(self)


class InOrderVerifiableInvocation(VerifiableInvocation):
    def __init__(self, mock, method_name, verification, inorder: InOrder):
        super().__init__(mock, method_name, verification)
        self._inorder = inorder

    def __call__(self, *params, **named_params):  # noqa: C901
        self._remember_params(params, named_params)

        ordered = self._inorder.ordered_invocations

        if not ordered:
            raise VerificationError(
                "\nThere are no recorded invocations."
            )

        # Find first invocation in global order that hasn't been used
        # for "in-order" verification yet.
        try:
            start_idx, next_invocation = next(
                (i, inv)
                for i, inv in enumerate(ordered)
                if not inv.verified_inorder
            )
        except StopIteration:
            raise VerificationError(
                "\nThere are no more recorded invocations."
            )

        called_mock = next_invocation.mock
        if called_mock is not self.mock:
            called_obj = mock_registry.obj_for(called_mock)
            if called_obj is None:
                raise RuntimeError(
                    f"{called_mock} is not in the registry (anymore)."
                )
            expected_obj = mock_registry.obj_for(self.mock)
            raise VerificationError(
                f"\nWanted a call from {expected_obj}, but "
                f"got {called_obj}.{next_invocation} instead!"
            )

        matched_invocations = []

        # Walk the contiguous block of this mock in the global queue.
        for inv in list(ordered)[start_idx:]:
            if inv.verified_inorder:
                continue
            if inv.mock is not self.mock:
                break

            if not self.matches(inv):
                raise VerificationError(
                    "\nWanted %s to be invoked,\n"
                    "got    %s instead." % (self, inv)
                )

            self.capture_arguments(inv)
            matched_invocations.append(inv)

        self.verification.verify(self, len(matched_invocations))

        for inv in matched_invocations:
            inv.verified = True
            inv.verified_inorder = True

        if verification_has_lower_bound_of_zero(self.verification):
            for stub in self.mock.stubbed_invocations:
                if stub.matches(self) or self.matches(stub):
                    stub.allow_zero_invocations = True
