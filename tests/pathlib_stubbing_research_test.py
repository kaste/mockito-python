import pathlib
import sys

import pytest

from mockito import mock, when
from mockito.invocation import InvocationError


pytestmark = pytest.mark.usefixtures("unstub")


def test_pathlib_factory_can_stub_exists_per_path_value():
    when(pathlib).Path("foo").exists().thenReturn(True)
    when(pathlib).Path("bar").exists().thenReturn(False)

    assert pathlib.Path("foo").exists() is True
    assert pathlib.Path("bar").exists() is False


def test_pathlib_factory_can_stub_read_text_per_path_value():
    when(pathlib).Path("foo").read_text().thenReturn("A")
    when(pathlib).Path("bar").read_text().thenReturn("B")

    assert pathlib.Path("foo").read_text() == "A"
    assert pathlib.Path("bar").read_text() == "B"


def test_pathlib_factory_can_return_path_doubles_with_parents_property():
    foo = mock({"parents": ["root", "foo"]}, spec=pathlib.Path)
    bar = mock({"parents": ["root", "bar"]}, spec=pathlib.Path)

    when(pathlib).Path("foo").thenReturn(foo)
    when(pathlib).Path("bar").thenReturn(bar)

    assert pathlib.Path("foo").parents == ["root", "foo"]
    assert pathlib.Path("bar").parents == ["root", "bar"]


@pytest.mark.xfail(reason="Not implemented", run=sys.version_info >= (3, 12))
def test_pathlib_factory_can_stub_parents_property_per_path_via_chaining():
    when(pathlib).Path("foo").parents.thenReturn(["root", "foo"])
    when(pathlib).Path("bar").parents.thenReturn(["root", "bar"])

    assert pathlib.Path("foo").parents == ["root", "foo"]
    assert pathlib.Path("bar").parents == ["root", "bar"]


@pytest.mark.xfail(reason="Not implemented", run=sys.version_info >= (3, 12))
def test_pathlib_factory_can_chain_through_parent_property_then_method():
    when(pathlib).Path("foo").parent.exists().thenReturn(True)

    assert pathlib.Path("foo").parent.exists() is True


def test_pathlib_factory_chain_can_distinguish_root_paths_with_operator_slash():
    when(pathlib).Path("foo").__truediv__("bar").exists().thenReturn(True)

    assert (pathlib.Path("foo") / "bar").exists() is True

    with pytest.raises(InvocationError):
        (pathlib.Path("bar") / "bar").exists()


def test_pathlib_factory_chain_segment_mismatch_should_scream_like_os_path():
    when(pathlib).Path("foo").__truediv__("bar").exists().thenReturn(True)

    with pytest.raises(InvocationError):
        (pathlib.Path("foo") / "baz").exists()


@pytest.mark.xfail(
    reason=(
        "Not implemented, not decided: decompose Path(*parts) constructor "
        "stubs into __truediv__ chain matching"
    ),
    run=sys.version_info >= (3, 12)
)
def test_pathlib_constructor_parts_stub_can_match_slash_composition():
    when(pathlib).Path("foo", "bar", "baz").exists().thenReturn(True)

    assert (pathlib.Path("foo") / "bar" / "baz").exists() is True


@pytest.mark.xfail(
    reason=(
        "Not implemented, not decided: treat Path('a/b/c') constructor "
        "stubs as segment-aware slash chains"
    ),
    run=sys.version_info >= (3, 12)
)
def test_pathlib_single_string_stub_can_match_slash_composition():
    when(pathlib).Path("foo/bar/baz").exists().thenReturn(True)

    assert (pathlib.Path("foo") / "bar" / "baz").exists() is True
