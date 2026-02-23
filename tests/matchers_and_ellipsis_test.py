import pytest

from mockito import args, kwargs, invocation, when


class C:
    def function(self, one, two):
        return (one, two)

    def variadic(self, one, *args, **kwargs):
        return (one, args, kwargs)

    def fetch(self, location, retry=5, **options):
        return (location, retry, options)

    def sum(self, *values, init=0):
        return init + sum(values)


def test_ellipsis_as_sole_argument_is_whatever_but_signature_still_applies(
    unstub,
):
    c = C()
    when(c).function(...).thenReturn("ok")

    assert c.function(1, 2) == "ok"
    assert c.function("1", 2) == "ok"

    with pytest.raises(TypeError):
        c.function()

    with pytest.raises(TypeError):
        c.function(1, 2, 3)


def test_trailing_ellipsis_is_rest_for_fixed_arity_functions(unstub):
    c = C()
    when(c).function(2, ...).thenReturn("ok")

    assert c.function(2, 2) == "ok"
    assert c.function(2, "22") == "ok"
    assert c.function(2, True) == "ok"

    with pytest.raises(TypeError):
        c.function(2, 3, 4)


def test_trailing_ellipsis_is_rest_for_variadic_functions(unstub):
    c = C()
    when(c).variadic(1, ...).thenReturn("ok")

    assert c.variadic(1) == "ok"
    assert c.variadic(1, 2) == "ok"
    assert c.variadic(1, 2, 3) == "ok"
    assert c.variadic(1, 2, three=3) == "ok"


def test_ellipsis_in_keyword_position_is_an_any_marker(unstub):
    c = C()
    url = "https://example.com/"
    when(c).fetch(url, retry=...).thenReturn("ok")

    assert c.fetch(url, retry=2) == "ok"
    assert c.fetch(url, retry=5) == "ok"

    with pytest.raises(invocation.InvocationError):
        c.fetch(url)

    with pytest.raises(invocation.InvocationError):
        c.fetch(url, headers={})


def test_fixed_ellipsis_plus_trailing_rest_allows_extra_keyword_arguments(unstub):
    c = C()
    url = "https://example.com/"
    when(c).fetch(url, retry=..., **kwargs).thenReturn("ok")

    assert c.fetch(url, retry=2, headers={}) == "ok"


def test_leading_fixed_ellipsis_plus_trailing_rest_example(unstub):
    c = C()
    when(c).fetch(..., retry=2, **kwargs).thenReturn("ok")

    assert c.fetch("https://example.com/", retry=2) == "ok"
    assert c.fetch("https://foobar.com/", retry=2) == "ok"
    assert c.fetch("https://foobar.com/", retry=2, headers={}) == "ok"


@pytest.mark.xfail(reason="Not implemented. Needs decision.")
def test_ellipsis_in_fixed_positions_consumes_exactly_one_value(unstub):
    c = C()
    when(c).fetch(..., ..., headers=...).thenReturn("ok")

    assert c.fetch("https://foobar.com/", 2, headers={}) == "ok"
    assert c.fetch("https://foobar.com/", retry=2, headers={}) == "ok"

    with pytest.raises(invocation.InvocationError):
        c.fetch("https://foobar.com/", headers={})


@pytest.mark.xfail(reason="Not implemented. Needs decision.")
def test_any_marker_form_matches_same_examples(unstub):
    c = C()
    when(c).fetch(any, any, headers=any).thenReturn("ok")

    assert c.fetch("https://foobar.com/", 2, headers={}) == "ok"
    assert c.fetch("https://foobar.com/", retry=2, headers={}) == "ok"


def test_args_matcher_consumes_zero_or_more_positional_arguments(unstub):
    c = C()
    when(c).sum(1, 2, *args).thenReturn("ok")

    assert c.sum(1, 2) == "ok"
    assert c.sum(1, 2, 3) == "ok"
    assert c.sum(1, 2, 3, 4) == "ok"


def test_ellipsis_rest_can_consume_zero_or_more_arguments(unstub):
    c = C()
    when(c).sum(1, 2, ...).thenReturn("ok")

    assert c.sum(1, 2) == "ok"
    assert c.sum(1, 2, 3) == "ok"


def test_args_matcher_can_be_combined_with_keywords(unstub):
    c = C()
    when(c).sum(1, 2, *args, init=5).thenReturn("ok")

    assert c.sum(1, 2, 3, init=5) == "ok"
    assert c.sum(1, 2, 3, 4, init=5) == "ok"


def test_fixed_ellipsis_before_keyword_consumes_exactly_one_value(unstub):
    c = C()
    when(c).sum(1, 2, ..., init=5).thenReturn("ok")

    assert c.sum(1, 2, 3, init=5) == "ok"

    with pytest.raises(invocation.InvocationError):
        c.sum(1, 2, init=5)

    with pytest.raises(invocation.InvocationError):
        c.sum(1, 2, 3, 4, init=5)
