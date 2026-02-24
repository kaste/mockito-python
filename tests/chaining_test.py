import pytest

from mockito import expect, mock, verify, when
from mockito.invocation import InvocationError


pytestmark = pytest.mark.usefixtures("unstub")


def test_can_stub_method_chain_leaf_return_value():
    cat = mock()

    when(cat).meow().purr().thenReturn("friendly")

    assert cat.meow().purr() == "friendly"


def test_method_chain_without_then_defaults_to_none_and_records_call():
    cat = mock()

    when(cat).meow().purr()

    cat_that_meowed = cat.meow()
    assert cat_that_meowed.purr() is None
    verify(cat_that_meowed).purr()


def test_multiple_chain_branches_on_same_root_are_supported():
    cat = mock()

    when(cat).meow().purr().thenReturn("friendly")
    when(cat).meow().roll().thenReturn("playful")

    cat_that_meowed = cat.meow()
    assert cat_that_meowed.purr() == "friendly"
    assert cat_that_meowed.roll() == "playful"


def test_expectation_on_chain_applies_to_leaf():
    cat = mock()

    expect(cat, times=1).meow().purr()

    cat.meow().purr()
    cat.meow()

    with pytest.raises(InvocationError):
        cat.meow().purr()


def test_chain_after_direct_return_configuration_is_rejected():
    cat = mock()

    when(cat).meow().thenReturn("meow!")

    with pytest.raises(InvocationError) as exc:
        when(cat).meow().purr()

    assert str(exc.value) == "'meow' is already configured with a direct answer."
    assert cat.meow() == "meow!"


def test_chain_after_direct_return_on_same_selector_is_rejected():
    cat = mock()

    answer_selector = when(cat).meow().thenReturn("meow!")

    with pytest.raises(InvocationError) as exc:
        answer_selector.purr()

    assert str(exc.value) == "'meow' is already configured with a direct answer."
    assert cat.meow() == "meow!"


def test_direct_return_after_chain_configuration_is_rejected():
    cat = mock()

    when(cat).meow().purr().thenReturn("purr")

    with pytest.raises(InvocationError) as exc:
        when(cat).meow().thenReturn("meow!")

    assert str(exc.value) == "'meow' is already configured for chained stubbing."
    assert cat.meow().purr() == "purr"


def test_direct_return_after_chain_on_same_selector_is_rejected():
    cat = mock()

    answer_selector = when(cat).meow()
    answer_selector.purr().thenReturn("purr")

    with pytest.raises(InvocationError) as exc:
        answer_selector.thenReturn("meow!")

    assert str(exc.value) == "'meow' is already configured for chained stubbing."
    assert cat.meow().purr() == "purr"


def test_property_chaining_is_supported():
    cat = mock()

    when(cat).age.value().thenReturn(14)
    when(cat).age.greater_than(12).thenReturn(True)

    assert cat.age.value() == 14
    assert cat.age.greater_than(12) is True


def test_context_manager_unwinds_method_chains_of_any_length():
    cat = mock()

    with when(cat).meow().purr().sleep().thenReturn("ok"):
        assert cat.meow().purr().sleep() == "ok"

    assert cat.meow() is None


def test_context_manager_unwinds_property_chains_of_any_length():
    class F:
        @property
        def p(self):
            return 42

    with when(F).p.a().b().thenReturn("ok"):
        assert F().p.a().b() == "ok"

    assert F().p == 42


def test_context_branch_cleanup_keeps_existing_sibling_chain_branch():
    cat = mock()

    when(cat).meow().purr().run().thenReturn("run")

    with when(cat).meow().purr().roll().thenReturn(None):
        assert cat.meow().purr().run() == "run"
        assert cat.meow().purr().roll() is None

    assert cat.meow().purr().run() == "run"


def test_context_same_path_temporarily_overrides_chain_leaf():
    cat = mock()

    when(cat).meow().purr().run().thenReturn("base")

    with when(cat).meow().purr().run().thenReturn("override"):
        assert cat.meow().purr().run() == "override"

    assert cat.meow().purr().run() == "base"


def test_chain_matching_ignores_unrelated_value_stubbed_methods():
    cat = mock()

    when(cat).sleep().thenReturn("sleep")
    when(cat).meow().purr().thenReturn("purr")

    assert cat.sleep() == "sleep"
    assert cat.meow().purr() == "purr"


def test_chain_matching_ignores_unrelated_chain_stubbed_methods():
    cat = mock()

    when(cat).meow().purr().thenReturn("purr")
    when(cat).roll().over().thenReturn("roll")

    assert cat.meow().purr() == "purr"
    assert cat.roll().over() == "roll"


def test_chain_matching_ignores_same_method_with_different_concrete_args():
    cat = mock()

    when(cat).meow(1).thenReturn("one")
    when(cat).meow(2).purr().thenReturn("two")

    assert cat.meow(1) == "one"
    assert cat.meow(2).purr() == "two"


def test_chain_matching_requires_existing_matches_candidate_direction():
    cat = mock()

    when(cat).meow(1).thenReturn("one")
    when(cat).meow(...).purr().thenReturn("many")

    assert cat.meow(2).purr() == "many"


def test_chain_matching_requires_candidate_matches_existing_direction():
    cat = mock()

    when(cat).meow(...).thenReturn("any")
    when(cat).meow(2).purr().thenReturn("two")

    assert cat.meow(1) == "any"
    assert cat.meow(2).purr() == "two"


