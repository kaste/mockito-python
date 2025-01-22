import pytest
from copy import copy, deepcopy
from mockito import mock, when


class TestDeepcopy:
    def test_dumb_mocks_are_copied_correctly(self):
        m = mock()
        m.foo = [1]
        n = deepcopy(m)
        assert m is not n
        assert n.foo == [1]

        m.foo.append(2)
        assert n.foo == [1]

    def test_strict_mocks_raise_on_unexpected_calls(self):
        m = mock(strict=True)
        with pytest.raises(RuntimeError) as exc:
            deepcopy(m)
        assert str(exc.value) == (
            "'Dummy' has no attribute '__deepcopy__' configured"
        )

    def test_configured_strict_mock_answers_correctly(self):
        m = mock(strict=True)
        when(m).__deepcopy__(...).thenReturn(42)
        assert deepcopy(m) == 42

    def test_setting_none_enables_the_standard_implementation(self):
        m = mock({"__deepcopy__": None}, strict=True)
        m.foo = [1]

        n = deepcopy(m)
        assert m is not n
        assert n.foo == [1]

        m.foo.append(2)
        assert n.foo == [1]


    @pytest.mark.xfail(reason=(
        "the configuration is set on the mock's class, not the instance, "
        "which deepcopy does not copy"
    ))
    def test_deepcopy_of_a_configured_mock_is_a_new_mock(self):
        m = mock({"foo": [1]}, strict=True)
        n = deepcopy(m)

        m.foo.append(2)
        assert n.foo == [1]



class TestCopy:
    def test_dumb_mocks_are_copied_correctly(self):
        m = mock()
        m.foo = [1]
        n = copy(m)
        assert m is not n
        assert n.foo == [1]

        m.foo.append(2)
        assert n.foo == [1, 2]

    @pytest.mark.xfail(reason=(
        "not working for `copy` because __copy__ is accessed on the class, "
        "not the instance"
    ))
    def test_strict_mocks_raise_on_unexpected_calls(self):
        m = mock(strict=True)
        with pytest.raises(RuntimeError) as exc:
            copy(m)
        assert str(exc.value) == (
            "'Dummy' has no attribute '__copy__' configured"
        )
