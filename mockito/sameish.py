from __future__ import annotations

from typing import TYPE_CHECKING

from . import matchers

if TYPE_CHECKING:
    from .invocation import StubbedInvocation


def invocations_are_sameish(
    left: StubbedInvocation,
    right: StubbedInvocation,
) -> bool:
    """Structural signature-compatibility checks for continuation bookkeeping.

    Intentionally avoids executing user-provided matcher predicates
    (e.g. `arg_that(...)) while comparing stub signatures.
    """

    return (
        _params_are_sameish(left.params, right.params)
        and _named_params_are_sameish(
            left.named_params,
            right.named_params,
        )
    )


def invocations_have_distinct_captors(
    left: StubbedInvocation,
    right: StubbedInvocation,
) -> bool:
    """Return True when equivalent selectors bind different captor instances."""

    for left_value, right_value in zip(left.params, right.params):
        if _values_bind_distinct_captors(left_value, right_value):
            return True

    for key in set(left.named_params) & set(right.named_params):
        if _values_bind_distinct_captors(
            left.named_params[key],
            right.named_params[key],
        ):
            return True

    return False


def _params_are_sameish(left: tuple, right: tuple) -> bool:
    if len(left) != len(right):
        return False

    return all(
        _values_are_sameish(left_value, right_value)
        for left_value, right_value in zip(left, right)
    )


def _named_params_are_sameish(left: dict, right: dict) -> bool:
    if set(left) != set(right):
        return False

    return all(
        _values_are_sameish(left[key], right[key])
        for key in left
    )


def _values_are_sameish(left: object, right: object) -> bool:
    if left is right:
        return True

    if left is Ellipsis or right is Ellipsis:
        return left is right

    if matchers.is_call_captor(left) and matchers.is_call_captor(right):
        return True

    if matchers.is_call_captor(left) or matchers.is_call_captor(right):
        return False

    if (
        matchers.is_captor_args_sentinel(left)
        and matchers.is_captor_args_sentinel(right)
    ):
        return _values_are_sameish(left.captor.matcher, right.captor.matcher)

    if (
        matchers.is_captor_kwargs_sentinel(left)
        and matchers.is_captor_kwargs_sentinel(right)
    ):
        return _values_are_sameish(left.captor.matcher, right.captor.matcher)

    if (
        matchers.is_captor_args_sentinel(left)
        or matchers.is_captor_args_sentinel(right)
        or matchers.is_captor_kwargs_sentinel(left)
        or matchers.is_captor_kwargs_sentinel(right)
    ):
        return False

    if isinstance(left, matchers.Matcher) and isinstance(right, matchers.Matcher):
        return _matchers_are_sameish(left, right)

    if isinstance(left, matchers.Matcher) or isinstance(right, matchers.Matcher):
        return False

    return _equals_or_identity(left, right)


def _matchers_are_sameish(  # noqa: C901
    left: matchers.Matcher,
    right: matchers.Matcher,
) -> bool:
    if left is right:
        return True

    if type(left) is not type(right):
        return False

    if isinstance(left, matchers.Any) and isinstance(right, matchers.Any):
        return _equals_or_identity(left.wanted_type, right.wanted_type)

    if (
        isinstance(left, matchers.ValueMatcher)
        and isinstance(right, matchers.ValueMatcher)
    ):
        return _values_are_sameish(left.value, right.value)

    if (
        isinstance(left, (matchers.And, matchers.Or))
        and isinstance(right, (matchers.And, matchers.Or))
    ):
        return _params_are_sameish(
            tuple(left.matchers),
            tuple(right.matchers),
        )

    if isinstance(left, matchers.Not) and isinstance(right, matchers.Not):
        return _values_are_sameish(left.matcher, right.matcher)

    if isinstance(left, matchers.ArgThat) and isinstance(right, matchers.ArgThat):
        return left.predicate is right.predicate

    if isinstance(left, matchers.Contains) and isinstance(right, matchers.Contains):
        return _values_are_sameish(left.sub, right.sub)

    if isinstance(left, matchers.Matches) and isinstance(right, matchers.Matches):
        return (
            left.regex.pattern == right.regex.pattern
            and left.flags == right.flags
        )

    if (
        isinstance(left, matchers.ArgumentCaptor)
        and isinstance(right, matchers.ArgumentCaptor)
    ):
        return _values_are_sameish(left.matcher, right.matcher)

    return _equals_or_identity(left, right)


def _values_bind_distinct_captors(left: object, right: object) -> bool:
    left_binding = _captor_binding(left)
    right_binding = _captor_binding(right)

    return (
        left_binding is not None
        and right_binding is not None
        and left_binding is not right_binding
    )


def _captor_binding(value: object) -> object | None:
    if matchers.is_call_captor(value):
        return value

    if isinstance(value, matchers.ArgumentCaptor):
        return value

    if matchers.is_captor_args_sentinel(value):
        return value.captor

    if matchers.is_captor_kwargs_sentinel(value):
        return value.captor

    return None


def _equals_or_identity(left: object, right: object) -> bool:
    try:
        return left == right
    except Exception:
        return left is right
