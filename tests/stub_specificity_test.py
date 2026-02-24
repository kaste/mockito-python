import pytest

from mockito import any, args, kwargs, mock, when


pytestmark = pytest.mark.usefixtures("unstub")


class _Path:
    def exists(self, location):
        return f"orig:{location}"


def test_literal_stub_beats_ellipsis_even_if_ellipsis_added_last():
    path = mock(_Path)

    when(path).exists(".flake8").thenReturn("stubbed")
    when(path).exists(...).thenCallOriginalImplementation()

    assert path.exists(".flake8") == "stubbed"
    assert path.exists("README.rst") == "orig:README.rst"


def test_literal_stub_beats_ellipsis_even_if_literal_added_last():
    path = mock(_Path)

    when(path).exists(...).thenCallOriginalImplementation()
    when(path).exists(".flake8").thenReturn("stubbed")

    assert path.exists(".flake8") == "stubbed"
    assert path.exists("README.rst") == "orig:README.rst"


def test_typed_any_is_more_specific_than_any_and_ellipsis():
    path = mock()

    when(path).exists(...).thenReturn("ellipsis")
    when(path).exists(any()).thenReturn("any")
    when(path).exists(any(str)).thenReturn("typed-any")

    assert path.exists(".flake8") == "typed-any"
    assert path.exists(1) == "any"


def test_any_and_ellipsis_have_same_specificity_and_keep_last_wins_tie_break():
    path = mock()

    when(path).exists(any()).thenReturn("any")
    when(path).exists(...).thenReturn("ellipsis")
    assert path.exists(1) == "ellipsis"

    other = mock()
    when(other).exists(...).thenReturn("ellipsis")
    when(other).exists(any()).thenReturn("any")
    assert other.exists(1) == "any"


def test_coverage_beats_quality_when_both_match():
    subject = mock()

    when(subject).f("x", ...).thenReturn("prefix")
    when(subject).f(..., retry=..., headers=...).thenReturn("kwargs-shape")

    assert subject.f("x", retry=5, headers={}) == "kwargs-shape"


def test_literal_beats_matchers_when_coverage_is_equal():
    subject = mock()

    when(subject).f("x", ...).thenReturn("prefix-fallback")
    when(subject).f(any(str), any(int)).thenReturn("typed-exact")

    assert subject.f("x", 1) == "prefix-fallback"


def test_args_and_kwargs_sentinels_have_same_weight_as_ellipsis():
    subject = mock()

    when(subject).f(...).thenReturn("ellipsis")
    when(subject).f(*args).thenReturn("args")

    assert subject.f(1) == "args"

    other = mock()
    when(other).g(...).thenReturn("ellipsis")
    when(other).g(**kwargs).thenReturn("kwargs")

    assert other.g(retry=1) == "kwargs"
