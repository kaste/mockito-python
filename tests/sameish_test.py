from dataclasses import dataclass, field

from mockito import and_, any as any_, arg_that, call_captor, eq, gt, neq, or_
from mockito import sameish


@dataclass
class FakeInvocation:
    params: tuple = ()
    named_params: dict = field(default_factory=dict)


def bar(*params, **named_params):
    return FakeInvocation(params=params, named_params=named_params)


def test_concrete_values_must_match_exactly():
    assert sameish.invocations_are_sameish(
        bar(1, "x"),
        bar(1, "x"),
    )
    assert not sameish.invocations_are_sameish(
        bar(1, "x"),
        bar(2, "x"),
    )


def test_keyword_names_must_match_independent_of_order():
    assert sameish.invocations_are_sameish(
        bar(a=1, b=2),
        bar(b=2, a=1),
    )
    assert not sameish.invocations_are_sameish(
        bar(a=1),
        bar(a=1, b=2),
    )


def test_any_matchers_are_compared_structurally():
    assert sameish.invocations_are_sameish(
        bar(any_(int)),
        bar(any_(int)),
    )
    assert not sameish.invocations_are_sameish(
        bar(any_(int)),
        bar(any_()),
    )
    assert not sameish.invocations_are_sameish(
        bar(any_()),
        bar(1),
    )


def test_composite_matchers_are_compared_recursively():
    assert sameish.invocations_are_sameish(
        bar(and_(any_(int), gt(1))),
        bar(and_(any_(int), gt(1))),
    )
    assert not sameish.invocations_are_sameish(
        bar(and_(any_(int), gt(1))),
        bar(and_(any_(int), gt(2))),
    )


def test_distinct_matcher_types_are_not_sameish_even_with_equal_payload():
    assert not sameish.invocations_are_sameish(
        bar(eq(1)),
        bar(neq(1)),
    )
    assert not sameish.invocations_are_sameish(
        bar(and_(any_(int), gt(1))),
        bar(or_(any_(int), gt(1))),
    )


def test_arg_that_uses_predicate_identity_and_does_not_execute_predicate():
    calls = []

    def predicate(value):
        calls.append(value)
        raise RuntimeError("must not be executed")

    assert sameish.invocations_are_sameish(
        bar(arg_that(predicate)),
        bar(arg_that(predicate)),
    )
    assert calls == []


def test_arg_that_with_different_predicates_is_not_sameish():
    assert not sameish.invocations_are_sameish(
        bar(arg_that(lambda value: value > 0)),
        bar(arg_that(lambda value: value > 0)),
    )


def test_arg_that_predicate_side_effects_are_not_triggered():
    seen = []

    def predicate(value):
        seen.append(value)
        return True

    assert sameish.invocations_are_sameish(
        bar(arg_that(predicate)),
        bar(arg_that(predicate)),
    )
    assert seen == []


def test_call_captor_instances_are_not_interchangeable():
    left = call_captor()
    right = call_captor()

    assert sameish.invocations_are_sameish(
        bar(left),
        bar(left),
    )
    assert not sameish.invocations_are_sameish(
        bar(left),
        bar(right),
    )


def test_eq_failures_fallback_to_identity():
    class EqBoom:
        def __eq__(self, other):
            raise RuntimeError("boom")

    first = EqBoom()
    second = EqBoom()

    assert sameish.invocations_are_sameish(
        bar(first),
        bar(first),
    )
    assert not sameish.invocations_are_sameish(
        bar(first),
        bar(second),
    )
