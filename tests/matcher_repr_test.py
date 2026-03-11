import re

from mockito import and_, any as any_, contains, eq, gt, matches, not_, or_


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
