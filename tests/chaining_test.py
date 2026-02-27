import pytest

from mockito import expect, mock, verify, unstub, when
from mockito.invocation import AnswerError, InvocationError


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


def test_unstub_child_chain_then_reconfigure_does_not_leave_stale_root_stub():
    cat = mock()

    when(cat).meow().purr().sleep().thenReturn("base")
    when(cat).meow().purr().sleep().thenReturn("override")

    with when(cat).meow().purr():
        cat.meow().purr()

    with pytest.raises(InvocationError) as exc:
        with when(cat).meow().purr().thenReturn("tmp"):
            cat.meow().purr()

    assert str(exc.value) == "'purr' is already configured for chained stubbing."

    unstub(cat.meow())

    with when(cat).meow().purr().thenReturn("tmp"):
        assert cat.meow().purr() == "tmp"

    assert cat.meow() is None


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

def test_deep_property_chain_with_method_leaf_is_supported():
    cat = mock()

    when(cat).age.expected.to.be(14).thenReturn(False)

    assert cat.age.expected.to.be(14) is False


def test_deep_property_chain_with_property_leaf_is_supported():
    cat = mock()

    when(cat).age.expected.to.value.thenReturn(14)

    assert cat.age.expected.to.value == 14


def test_deep_property_chain_method_and_property_leaf_can_coexist():
    cat = mock()

    when(cat).age.expected.to.be(14).thenReturn(False)
    when(cat).age.expected.to.value.thenReturn(14)

    assert cat.age.expected.to.be(14) is False
    assert cat.age.expected.to.value == 14


def test_unconfigured_context_manager_rewinds_1():
    cat = mock()

    assert cat.age() is None

    with pytest.raises((TypeError, AttributeError)):
        with when(cat).age.expected.to.thenReturn:
            pass

    assert cat.age() is None


def test_unconfigured_context_manager_rewinds_2():
    cat = mock()

    assert cat.age() is None

    with pytest.raises((TypeError, AttributeError)):
        with when(cat).age.expected.to.leaf:
            pass

    assert cat.age() is None


def test_failed_call_original_rewinds_1():
    cat = mock()
    with pytest.raises(AnswerError):
        when(cat).age.expected.to.value.thenCallOriginalImplementation()

    assert cat.age() is None


def test_failed_call_original_rewinds_2():
    cat = mock()
    with pytest.raises(AnswerError):
        when(cat).age.expected.to.be(14).thenCallOriginalImplementation()

    assert cat.age() is None


def test_failed_call_original_on_deep_property_leaf_rolls_back_only_leaf():
    cat = mock()

    when(cat).age.expected.to.be(14).thenReturn(False)
    when(cat).age.expected.to.value.thenReturn(14)

    with pytest.raises(AnswerError) as exc:
        when(cat).age.expected.to.value.thenCallOriginalImplementation()

    assert str(exc.value) == (
        "'<class 'mockito.mocking.mock.<locals>.Dummy'>' "
        "has no original implementation for 'value'."
    )
    assert cat.age.expected.to.be(14) is False
    assert cat.age.expected.to.value == 14


def test_a():
    cat = mock()
    assert cat.our() is None

    with when(cat).our.cat.named("spooky").is_very.brave.thenReturn(True):
        assert cat.our.cat.named("spooky").is_very.brave is True

    assert cat.our() is None
    with when(cat).our.cat.named("spooky").is_very.brave.thenReturn(True):
        assert cat.our.cat.named("spooky").is_very.brave is True

    assert cat.our() is None


def test_b():
    cat = mock()
    assert cat.our() is None

    with pytest.raises(AnswerError):
        with when(cat).our.cat.named("spooky") \
                .is_very.brave.thenCallOriginalImplementation():
            ...

    assert cat.our() is None


def test_c():
    cat = mock()
    assert cat.our() is None

    with pytest.raises(AnswerError):
        when(cat).our.cat.named("spooky").is_very.brave.thenCallOriginalImplementation()

    assert cat.our() is None


def test_d():
    cat = mock()
    assert cat.our() is None

    when(cat).our.cat.named("spooky")
    with pytest.raises(AnswerError):
        when(cat).our.cat.named("spooky").is_very.brave.thenCallOriginalImplementation()

    assert cat.our
    assert cat.our.cat.named("spooky") is None


def test_e1():
    cat = mock()
    assert cat.our() is None

    with when(cat).our.cat.named("spooky") \
            .is_very.brave.thenReturn(True).thenReturn(False):
        assert cat.our.cat.named("spooky").is_very.brave is True
        assert cat.our.cat.named("spooky").is_very.brave is False
        assert cat.our.cat.named("spooky").is_very.brave is False

    assert cat.our() is None


def test_e2():
    cat = mock()
    assert cat.our() is None

    when(cat).our.cat.named("spooky")
    assert cat.our.cat.named("spooky") is None

    when(cat).our.cat.named("spooky").is_very.brave.thenReturn(True).thenReturn(False)
    assert cat.our.cat.named("spooky") is not None

    unstub(cat)
    assert cat.our() is None


def test_e3():
    cat = mock()
    assert cat.our() is None

    when(cat).our.cat.named("spooky").is_very.brave.thenReturn(True).thenReturn(False)
    assert cat.our.cat.named("spooky") is not None

    unstub(cat.our.cat)
    with pytest.raises(AttributeError):
        assert cat.our.cat.named("spooky") is not None


def test_f():
    cat = mock()
    assert cat.our() is None

    with pytest.raises(AttributeError):
        with when(cat).our.cat.named("spooky") \
                .is_very.brave.thenReturn(True).otherwise.null:
            ...

    assert cat.our() is None


def test_g1():   # for illustration
    cat = mock(strict=False)
    assert hasattr(cat, "your") is True
    assert cat.your  # okay, not strict


def test_g1b():   # for illustration
    cat = mock(strict=False)
    expect(cat).your  # <== doesn't change anything
    assert hasattr(cat, "your") is True
    assert cat.your


def test_g2():   # for illustration
    cat = mock(strict=True)
    assert hasattr(cat, "your") is False
    with pytest.raises(AttributeError):
        assert cat.your   # 'your' is not configured


def test_g2b():   # for illustration
    cat = mock(strict=True)
    expect(cat).your  # <== doesn't change anything
    assert hasattr(cat, "your") is False
    with pytest.raises(AttributeError):
        assert cat.your   # 'your' is not configured


@pytest.mark.xfail(reason="Needs decision")
def test_g3_non_strict_chain_child_stays_non_strict():
    cat = mock(strict=False)

    when(cat).our.cat.named("spooky").is_spooky

    spooky = cat.our.cat.named("spooky")
    assert spooky is not None
    assert hasattr(spooky, "is_spooky") is True
    assert spooky.is_spooky


@pytest.mark.xfail(reason="Not implemented")
def test_g4_strict_chain_child_stays_strict():
    cat = mock(strict=True)

    when(cat).our.cat.named("spooky").is_spooky

    spooky = cat.our.cat.named("spooky")
    assert spooky is not None
    assert hasattr(spooky, "is_spooky") is False
    with pytest.raises(AttributeError):  # 'Dummy' has no attribute 'is_spooky' ...
        assert spooky.is_spooky


@pytest.mark.xfail(reason="Not implemented")
def test_g5_ensure_we_unwind_to_previous_state():
    cat = mock()
    expect(cat).our.cat.named("spooky")
    assert cat.our.cat.named("spooky") is None

    with expect(cat).our.cat.named("spooky").is_spooky:
        assert cat.our.cat.named("spooky") is not None

    assert cat.our.cat.named("spooky") is None


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


def test_unexpected_chain_segment_arguments_raise_invocation_error_early():
    cat = mock()

    when(cat).meow().jump("bar").sleep().thenReturn("ok")

    with pytest.raises(InvocationError) as exc:
        cat.meow().jump("baz").sleep()

    assert str(exc.value) == (
        "\nCalled but not expected:\n"
        "\n"
        "    jump('baz')\n"
        "\n"
        "Stubbed invocations are:\n"
        "\n"
        "    jump('bar')\n"
        "\n"
    )

