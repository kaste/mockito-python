from functools import partial
import re

import numpy as np

from mockito import and_, any as any_, arg_that, contains, eq, gt, matches, not_, or_


def test_value_matchers_use_repr_for_string_values():
    assert repr(eq("foo")) == "<Eq: 'foo'>"


def test_composed_matchers_include_quoted_nested_values():
    assert repr(not_(eq("foo"))) == "<Not: <Eq: 'foo'>>"
    assert repr(and_(eq("foo"), gt(1))) == "<And: [<Eq: 'foo'>, <Gt: 1>]>"
    assert repr(or_(eq("foo"), gt(1))) == "<Or: [<Eq: 'foo'>, <Gt: 1>]>"


def test_any_repr_quotes_non_type_values():
    assert repr(any_("foo")) == "<Any: 'foo'>"


def test_contains_repr_uses_safe_quoted_substring():
    assert repr(contains("a'b")) == "<Contains: \"a'b\">"


def test_matches_repr_shows_only_explicit_flags():
    assert repr(matches("f..")) == "<Matches: 'f..'>"
    assert repr(matches("f..", re.IGNORECASE)) == (
        f"<Matches: 'f..' flags={int(re.IGNORECASE)}>"
    )


def test_arg_that_repr_includes_named_function_name():
    # Predicate display name: "def is_positive"
    def is_positive(value):
        return value > 0

    matcher = arg_that(is_positive)

    assert repr(matcher) == (
        f"<ArgThat: def is_positive at line {is_positive.__code__.co_firstlineno}>"
    )


def test_arg_that_repr_includes_lambda_name():
    # Predicate display name: "lambda"
    predicate = lambda value: value > 0
    matcher = arg_that(predicate)

    assert repr(matcher) == (
        f"<ArgThat: lambda at line {predicate.__code__.co_firstlineno}>"
    )


def test_arg_that_repr_for_callable_instance_includes_class_name():
    # Predicate display name: "callable IsPositive.__call__"
    class IsPositive:
        def __call__(self, value):
            return value > 0

    predicate = IsPositive()
    matcher = arg_that(predicate)

    assert repr(matcher) == (
        "<ArgThat: callable IsPositive.__call__ at line "
        f"{predicate.__call__.__func__.__code__.co_firstlineno}>"
    )


def test_arg_that_repr_for_builtin_callable_has_no_line_number():
    matcher = arg_that(len)

    assert repr(matcher) == "<ArgThat: def len>"


def test_arg_that_repr_for_partial_uses_underlying_function_name():
    predicate = partial(pow, exp=2)
    matcher = arg_that(predicate)

    assert repr(matcher) == "<ArgThat: partial pow>"


def test_arg_that_repr_for_numpy_ufunc_uses_function_name_without_line():
    matcher = arg_that(np.isfinite)

    assert repr(matcher) == "<ArgThat: def isfinite>"


def test_arg_that_repr_for_partial_numpy_function_uses_wrapped_name():
    predicate = partial(np.allclose, b=0.0)
    matcher = arg_that(predicate)

    assert repr(matcher) == "<ArgThat: partial allclose>"


def test_arg_that_repr_handles_callables_with_broken_name_introspection():
    class BrokenNameCallable:
        def __getattribute__(self, name):
            if name == '__name__':
                raise RuntimeError("boom")
            return super().__getattribute__(name)

        def __call__(self, value):
            return value > 0

    matcher = arg_that(BrokenNameCallable())

    matcher_repr = repr(matcher)
    assert matcher_repr.startswith("<ArgThat: callable BrokenNameCallable")
    assert "__name__" not in matcher_repr
