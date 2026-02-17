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

import ast
import inspect
from collections import deque
from functools import partial
from typing import Deque, TYPE_CHECKING

from .verification import VerificationError
from .invocation import RealInvocation, VerifiableInvocation
from .mockito import ArgumentError, verify as verify_main
from .mock_registry import mock_registry
from .utils import deprecated

if TYPE_CHECKING:
    from .mocking import Mock


@deprecated(
    "'inorder.verify' is deprecated. "
    "Use 'InOrder(...).verify(...)' instead."
)
def verify(object, *args, **kwargs):
    kwargs['inorder'] = True
    return verify_main(object, *args, **kwargs)


class InOrder:
    """Verify interactions in strict order across one or multiple objects.

    This is the preferred API for order-sensitive verification. `InOrder`
    keeps one global queue of recorded invocations for all observed objects,
    then verifies against that queue from left to right.

    Basic usage::

        from mockito import mock, InOrder

        cat = mock()
        dog = mock()

        in_order = InOrder(cat, dog)
        cat.meow()
        dog.bark()

        in_order.verify(cat).meow()
        in_order.verify(dog).bark()

    `InOrder.verify` uses the same fluent style and verification arguments as
    :func:`verify`, including ``times``, ``atleast``, ``atmost`` and
    ``between``::

        in_order.verify(cat, times=2).meow(...)
        in_order.verify(dog, between=(1, 3)).bark()

    Zero-lower-bound verifications (e.g. ``times=0`` or ``between=(0, 2)``)
    may pass without consuming the next queued invocation.

    `InOrder` can be used as a context manager::

        with InOrder(cat, dog) as in_order:
            cat.meow()
            dog.bark()
            in_order.verify(cat).meow()
            in_order.verify(dog).bark()

    Only the objects passed to `InOrder` are observed. Calls on other objects
    are ignored. Registration is dynamic: objects that are stubbed after
    `InOrder(...)` construction are still captured while the instance is active.

    See related :func:`verify`, :func:`expect`,
    :func:`ensureNoUnverifiedInteractions`, and
    :func:`verifyStubbedInvocationsAreUsed`.

    """

    def __init__(self, *objects: object) -> None:
        self._core = InOrderImpl(*objects)

    def verify(
        self,
        obj: object,
        times=None,
        atleast=None,
        atmost=None,
        between=None,
    ):
        return self._core.verify(
            obj,
            times=times,
            atleast=atleast,
            atmost=atmost,
            between=between,
        )

    def __enter__(self):
        self._core.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._core.__exit__(exc_type, exc_val, exc_tb)


class InOrderImpl:
    """Internal implementation behind the public `InOrder` facade."""


    def __init__(self, *objects: object):
        objects_: list[object] = []
        for obj in objects:
            if any(observed is obj for observed in objects_):
                raise ValueError(f"{obj} is provided more than once")
            objects_.append(obj)
        self._objects = objects_
        self._object_labels = self._guess_object_labels_from_callsite(
            len(objects_)
        )
        self._active = True
        self._observer_registered = False
        self.ordered_invocations: Deque[RealInvocation] = deque()

        self._register_observer()
        self._attach_all()

    def _is_observed(self, obj: object) -> bool:
        return any(observed is obj for observed in self._objects)

    def _register_observer(self) -> None:
        if not self._observer_registered:
            mock_registry.add_register_observer(self._on_mock_registered)
            self._observer_registered = True

    def _unregister_observer(self) -> None:
        if self._observer_registered:
            mock_registry.remove_register_observer(self._on_mock_registered)
            self._observer_registered = False

    def _attach_all(self):
        for obj in self._objects:
            if m := mock_registry.mock_for(obj):
                m.attach(self)

    def _detach_all(self) -> None:
        for obj in self._objects:
            if m := mock_registry.mock_for(obj):
                m.detach(self)

    def _on_mock_registered(self, obj: object, mock: Mock) -> None:
        if self._active and self._is_observed(obj):
            mock.attach(self)

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

        if not self._is_observed(obj):
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

    def close(self) -> None:
        self._active = False
        self._detach_all()
        self._unregister_observer()

    def __enter__(self):
        self._active = True
        self._register_observer()
        self._attach_all()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _callsite_label_for_obj(self, obj: object) -> str | None:
        for observed, label in zip(self._objects, self._object_labels):
            if observed is obj:
                return label
        return None

    def _label_for_obj(self, obj: object) -> str:
        if label := self._callsite_label_for_obj(obj):
            return label
        return str(obj)

    def _label_for_mock(self, mock: Mock) -> str:
        obj = mock_registry.obj_for(mock)
        if obj is None:
            return str(mock)
        return self._label_for_obj(obj)

    def _format_invocation(self, mock: Mock, invocation: object) -> str:
        if len(self._objects) == 1:
            return str(invocation)
        return f"{self._label_for_mock(mock)}.{invocation}"

    def _guess_object_labels_from_callsite(self, count: int) -> list[str | None]:
        if count == 0:
            return []

        # For a single observed object, object qualification adds little value
        # to mismatch messages (there is no cross-object ambiguity anyway).
        if count == 1:
            return [None]

        frame = inspect.currentframe()
        # Start at the direct caller and then walk out of our own module.
        # This is important because public `InOrder` delegates to `InOrderImpl`,
        # so the first stack frames are internal wrappers.
        caller_frame = frame.f_back if frame else None
        while caller_frame and caller_frame.f_code.co_filename == __file__:
            caller_frame = caller_frame.f_back

        if caller_frame is None:
            return [None] * count

        try:
            source_lines, start_lineno = inspect.getsourcelines(
                caller_frame.f_code
            )
            source = ''.join(source_lines)
            call_lineno = caller_frame.f_lineno - start_lineno + 1
            tree = ast.parse(source)
        except (OSError, TypeError, SyntaxError):
            return [None] * count
        finally:
            del frame
            del caller_frame

        call = self._find_inorder_call_for_lineno(tree, call_lineno)
        if call is None:
            return [None] * count

        labels: list[str | None] = []
        for arg in call.args[:count]:
            segment = ast.get_source_segment(source, arg)
            labels.append(segment.strip() if segment else None)

        if len(labels) < count:
            labels.extend([None] * (count - len(labels)))

        return labels

    def _find_inorder_call_for_lineno(
        self,
        tree: ast.AST,
        lineno: int,
    ) -> ast.Call | None:
        candidate: ast.Call | None = None
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if not self._is_inorder_constructor_call(node):
                continue

            start = node.lineno
            end = getattr(node, 'end_lineno', node.lineno)
            if start <= lineno <= end:
                # Ambiguous callsite (e.g. nested / same-line InOrder calls):
                # bail out.
                if candidate is not None:
                    return None

                candidate = node

        return candidate

    def _is_inorder_constructor_call(self, node: ast.Call) -> bool:
        if isinstance(node.func, ast.Name):
            return node.func.id == 'InOrder'

        if isinstance(node.func, ast.Attribute):
            return node.func.attr == 'InOrder'

        return False


class InOrderVerifiableInvocation(VerifiableInvocation):
    def __init__(self, mock, method_name, verification, inorder: InOrderImpl):
        super().__init__(mock, method_name, verification)
        self._inorder = inorder

    def __call__(self, *params, **named_params):  # noqa: C901
        self._remember_params(params, named_params)

        ordered = self._inorder.ordered_invocations

        if not ordered:
            if self.handle_zero_matches_if_allowed():
                return
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
            if self.handle_zero_matches_if_allowed():
                return
            raise VerificationError(
                "\nThere are no more recorded invocations."
            )

        called_mock = next_invocation.mock
        if called_mock is not self.mock:
            if self.handle_zero_matches_if_allowed():
                return
            if mock_registry.obj_for(called_mock) is None:
                raise RuntimeError(
                    f"{called_mock} is not in the registry (anymore)."
                )

            expected_obj = mock_registry.obj_for(self.mock)
            expected_has_callsite_label = (
                expected_obj is not None
                and self._inorder._callsite_label_for_obj(expected_obj)
            )
            got = self._inorder._format_invocation(called_mock, next_invocation)

            if expected_has_callsite_label:
                wanted = self._inorder._format_invocation(self.mock, self)
                raise VerificationError(
                    "\nWanted %s to be invoked,"
                    "\ngot    %s instead." % (wanted, got)
                )

            raise VerificationError(
                f"\nWanted a call from {expected_obj},"
                f"\ngot    {got} instead."
            )

        matched_invocations: list[RealInvocation] = []

        # Walk the contiguous block of this mock in the global queue.
        for inv in list(ordered)[start_idx:]:
            if inv.verified_inorder:
                continue
            if inv.mock is not self.mock:
                break

            if not self.matches(inv):
                if not matched_invocations:
                    if self.handle_zero_matches_if_allowed():
                        return
                    raise VerificationError(
                        "\nWanted %s to be invoked,"
                        "\ngot    %s instead." % (self, inv)
                    )
                break

            self.capture_arguments(inv)
            matched_invocations.append(inv)

        self.verification.verify(self, len(matched_invocations))

        for inv in matched_invocations:
            inv.verified = True
            inv.verified_inorder = True

        self.maybe_check_stubs_as_used()

    def handle_zero_matches_if_allowed(self) -> bool:
        if not self.verification_allows_zero_matches:
            return False

        self.verification.verify(self, 0)
        self.maybe_check_stubs_as_used()
        return True
