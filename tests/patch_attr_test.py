import gc
from io import StringIO
import sys
import weakref

import pytest

from mockito import mock, patch_attr, unstub, verify, when


pytestmark = pytest.mark.usefixtures("unstub")


class Holder:
    value = "original"


def test_patch_attr_by_dotted_path():
    original_argv = sys.argv
    replacement_argv = ["foo", "bar"]

    patch_attr("sys.argv", replacement_argv)
    assert sys.argv is replacement_argv

    unstub(sys)
    assert sys.argv is original_argv


def test_patch_attr_context_manager_returns_replacement_and_restores_on_exit():
    original_stdout = sys.stdout
    replacement_stdout = StringIO()

    with patch_attr("sys.stdout", replacement_stdout) as stdout:
        assert stdout is replacement_stdout
        assert sys.stdout is replacement_stdout

    assert sys.stdout is original_stdout


def test_patch_attr_replacement_can_be_configured_in_mockito_within_context():
    with patch_attr(sys, "stdout", mock()) as stdout:
        when(stdout).write("foo").thenReturn(3)

        assert sys.stdout.write("foo") == 3
        verify(stdout).write("foo")


def test_patch_attr_can_be_unstubbed_by_replacement_object():
    holder = Holder()
    replacement_value = object()

    patch_attr(holder, "value", replacement_value)
    assert holder.value is replacement_value

    unstub(holder.value)
    assert holder.value == "original"


def test_nested_patch_attr_restores_correctly():
    holder = Holder()

    with patch_attr(holder, "value", "first"):
        assert holder.value == "first"

        with patch_attr(holder, "value", "second"):
            assert holder.value == "second"

        assert holder.value == "first"

    assert holder.value == "original"


def test_unstub_after_when_then_patch_attr_restores_real_method():
    class LocalHolder:
        def value(self):
            return "original"

    holder = LocalHolder()

    when(holder).value().thenReturn("stubbed")
    patch_attr(holder, "value", lambda: "patched")

    unstub()
    assert holder.value() == "original"


def test_unstub_after_patch_attr_then_when_restores_real_method():
    class LocalHolder:
        def value(self):
            return "original"

    holder = LocalHolder()

    patch_attr(holder, "value", lambda: "patched")
    when(holder).value().thenReturn("stubbed")

    unstub()
    assert holder.value() == "original"


def test_nested_patch_attr_over_stubbed_method_restores_real_method():
    class LocalHolder:
        def value(self):
            return "original"

    holder = LocalHolder()

    when(holder).value().thenReturn("stubbed")
    patch_attr(holder, "value", lambda: "first")
    patch_attr(holder, "value", lambda: "second")

    unstub()
    assert holder.value() == "original"


def test_patch_attr_restores_inherited_lookup_without_shadowing_instance_attr():
    class Parent:
        value = "parent"

    class Child(Parent):
        pass

    child = Child()
    assert "value" not in child.__dict__

    with patch_attr(child, "value", "patched"):
        assert child.value == "patched"

    assert "value" not in child.__dict__

    Parent.value = "updated"
    assert child.value == "updated"


def test_patch_attr_restores_instance_data_descriptor_value():
    class HolderWithProperty:
        def __init__(self):
            self._value = "original"

        @property
        def value(self):
            return self._value

        @value.setter
        def value(self, value):
            self._value = value

    holder = HolderWithProperty()

    patch_attr(holder, "value", "patched")
    assert holder.value == "patched"

    unstub(holder)
    assert holder.value == "original"


def test_patch_attr_failed_apply_does_not_keep_target_alive():
    class DenyAttributeWrites:
        def __setattr__(self, name, value):
            raise TypeError("read-only")

    target = DenyAttributeWrites()
    replacement = Holder()

    target_ref = weakref.ref(target)
    replacement_ref = weakref.ref(replacement)

    with pytest.raises(TypeError):
        patch_attr(target, "value", replacement)

    del target
    del replacement
    gc.collect()

    assert target_ref() is None
    assert replacement_ref() is None
