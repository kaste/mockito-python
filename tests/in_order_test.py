import gc
import weakref

import pytest

from mockito import expect, mock, ArgumentError, VerificationError
from mockito.inorder import InOrder
from mockito import verify
from mockito.mock_registry import mock_registry


class Dog:
    def say(self, what):
        return what

    def __str__(self):
        return "<Dog>"


class EqualDog(Dog):
    def __eq__(self, other):
        return isinstance(other, EqualDog)


def test_observing_the_same_mock_twice_should_raise():
    a = mock()
    with pytest.raises(ValueError) as e:
        InOrder(a, a)
    assert str(e.value) == f"{a} is provided more than once"


def test_observing_the_same_mock_twice_should_raise_unhashable_obj():
    a = dict()  # type: ignore[var-annotated]
    with pytest.raises(ValueError):
        InOrder(a, a)


def test_observing_distinct_but_equal_objects_should_not_raise():
    a = EqualDog()
    b = EqualDog()
    InOrder(a, b)


def test_verifying_equal_but_not_observed_object_should_raise_not_part_of_inorder():
    observed = EqualDog()
    not_observed = EqualDog()

    expect(observed).say(...)
    expect(not_observed).say(...)

    in_order = InOrder(observed)

    with pytest.raises(ArgumentError) as e:
        in_order.verify(not_observed).say(...)

    assert str(e.value) == (
        f"\n{not_observed} is not part of that InOrder."
    )


def test_correct_order_declaration_should_pass():
    cat = mock()
    dog = mock()

    in_order: InOrder = InOrder(cat, dog)
    cat.meow()
    dog.bark()

    in_order.verify(cat).meow()
    in_order.verify(dog).bark()


def test_incorrect_order_declaration_should_fail():
    dog = mock()
    cat = mock()

    in_order: InOrder = InOrder(cat, dog)
    dog.bark()
    cat.meow()

    with pytest.raises(VerificationError) as e:
        in_order.verify(cat).meow()
    assert str(e.value) == (
        f"\nWanted a call from {cat}, but got "
        f"{dog}.bark() instead!"
    )


def test_error_message_for_unknown_objects():
    bob = Dog()
    bob.say("Grrr!")
    with InOrder(bob) as in_order:
        with pytest.raises(ArgumentError) as e:
            in_order.verify(bob).say("Wuff!")
    assert str(e.value) == (
        f"\n{bob} is not setup with any stubbings or expectations."
    )

def test_error_message_if_queue_was_never_not_empty():
    bob = Dog()
    expect(bob).say(...)
    with InOrder(bob) as in_order:
        with pytest.raises(VerificationError) as e:
            in_order.verify(bob).say(...)

    assert str(e.value) == (
        "\nThere are no recorded invocations."
    )


def test_capture_calls_after_late_mock_registration():
    bob = Dog()

    in_order = InOrder(bob)

    expect(bob).say(...)
    bob.say("Wuff!")

    in_order.verify(bob).say(...)


def test_register_observer_is_cleaned_up_automatically_on_gc():
    baseline = len(mock_registry._register_observers)

    in_order = InOrder(Dog())
    assert len(mock_registry._register_observers) == baseline + 1

    in_order_ref = weakref.ref(in_order)
    del in_order
    gc.collect()

    assert in_order_ref() is None

    # Trigger observer pruning.
    mock()

    assert len(mock_registry._register_observers) == baseline


def test_error_message_if_queue_is_empty():
    bob = Dog()
    rob = Dog()
    expect(bob).say(...)
    expect(rob).say(...)
    with InOrder(bob, rob) as in_order:
        bob.say("Wuff!")
        in_order.verify(bob).say(...)
        with pytest.raises(VerificationError) as e:
            in_order.verify(rob).say(...)

    assert str(e.value) == (
        "\nThere are no more recorded invocations."
    )

def test_verifing_not_observed_mocks_should_raise():
    cat = mock()
    to_ignore = mock()

    in_order: InOrder = InOrder(cat)
    to_ignore.bark()

    with pytest.raises(ArgumentError) as e:
        in_order.verify(to_ignore).bark()
    assert str(e.value) == (
        f"\n{to_ignore} is not part of that InOrder."
    )

def test_can_verify_multiple_orders():
    cat = mock()
    dog = mock()


    in_order: InOrder = InOrder(cat, dog)
    cat.meow()
    dog.bark()
    cat.meow()

    in_order.verify(cat).meow()
    in_order.verify(dog).bark()
    in_order.verify(cat).meow()

def test_can_verify_multiple_arguments():
    cat = mock()
    dog = mock()

    in_order: InOrder = InOrder(cat, dog)
    cat.meow("Meow!")
    dog.bark()
    cat.meow("Rrrr")

    in_order.verify(cat).meow("Meow!")
    in_order.verify(dog).bark()
    in_order.verify(cat).meow("Rrrr")


def test_can_verify_contiguous_calls_with_argument_checking():
    cat = mock()

    in_order = InOrder(cat)
    cat.meow("a")
    cat.meow("b")

    in_order.verify(cat).meow("a")
    in_order.verify(cat).meow("b")


def test_verifying_more_contiguous_calls_than_recorded_should_raise():
    cat = mock()

    in_order = InOrder(cat)
    cat.meow("a")
    cat.meow("b")

    in_order.verify(cat).meow("a")
    in_order.verify(cat).meow("b")

    with pytest.raises(VerificationError) as e:
        in_order.verify(cat).meow("a")

    assert str(e.value) == "\nThere are no more recorded invocations."


def test_first_contiguous_call_argument_mismatch_should_raise():
    cat = mock()

    in_order = InOrder(cat)
    cat.meow("a")
    cat.meow("b")

    with pytest.raises(VerificationError) as e:
        in_order.verify(cat).meow("b")

    assert str(e.value) == (
        "\nWanted meow('b') to be invoked,"
        "\ngot    meow('a') instead."
    )


def test_in_order_context_manager():
    cat = mock()
    dog = mock()

    with InOrder(cat, dog) as in_order:
        cat.meow()
        dog.bark()

        in_order.verify(cat).meow()
        in_order.verify(dog).bark()


def test_exiting_context_manager_should_detatch_mocks():
    cat = mock()
    dog = mock()

    with InOrder(cat, dog) as in_order:
        cat.meow()
        dog.bark()

        in_order.verify(cat).meow()
        in_order.verify(dog).bark()

    # can still verify after leaving the context manager
    verify(cat, times=1).meow()
    verify(dog).bark()


def test_do_not_record_after_detach():
    cat = mock()
    with InOrder(cat) as in_order:
        pass
    cat.meow()
    with pytest.raises(VerificationError):
        in_order.verify(cat).meow()


def test_allow_double_entrance():
    cat = mock()
    in_order = InOrder(cat)
    with in_order:
        pass
    cat.meow()
    with in_order:
        cat.meow()
    in_order.verify(cat, times=1).meow()


def test_close_should_detach_and_stop_late_registration_capture():
    bob = Dog()

    in_order = InOrder(bob)
    in_order.close()
    in_order.close()

    expect(bob).say(...)
    bob.say("Wuff!")

    with pytest.raises(VerificationError) as e:
        in_order.verify(bob).say(...)

    assert str(e.value) == "\nThere are no recorded invocations."


def test_in_order_verify_times_across_mocks():
    cat = mock()
    dog = mock()

    in_order: InOrder = InOrder(cat, dog)
    cat.meow()
    dog.bark()
    cat.meow()
    cat.meow()

    in_order.verify(cat, times=1).meow()
    in_order.verify(dog).bark()
    in_order.verify(cat, times=2).meow()


def test_in_order_verify_atleast():
    cat = mock()
    dog = mock()

    in_order: InOrder = InOrder(cat, dog)
    cat.meow()
    cat.meow()
    cat.meow()
    dog.bark()
    cat.meow()

    in_order.verify(cat, atleast=2).meow()
    in_order.verify(dog).bark()
    in_order.verify(cat, atleast=1).meow()


def test_in_order_verify_atmost():
    cat = mock()
    dog = mock()

    in_order: InOrder = InOrder(cat, dog)
    cat.meow()
    cat.meow()
    dog.bark()
    cat.meow()

    in_order.verify(cat, atmost=2).meow()
    in_order.verify(dog).bark()
    in_order.verify(cat, atmost=1).meow()


def test_in_order_verify_between():
    cat = mock()
    dog = mock()

    in_order: InOrder = InOrder(cat, dog)
    cat.meow()
    cat.meow()
    dog.bark()
    cat.meow()
    cat.meow()

    in_order.verify(cat, between=(1, 3)).meow()
    in_order.verify(dog).bark()
    in_order.verify(cat, between=(1, 3)).meow()


@pytest.mark.parametrize(
    "verify_kwargs",
    [
        {"times": 0},
        {"between": (0, 2)},
    ],
    ids=["times_0", "between_0_2"],
)
def test_in_order_verify_zero_lower_bound_does_not_fail_on_other_mock(
    verify_kwargs,
):
    cat = mock()
    dog = mock()

    in_order: InOrder = InOrder(cat, dog)
    dog.bark()

    in_order.verify(cat, **verify_kwargs).meow()
    in_order.verify(dog).bark()


@pytest.mark.parametrize(
    "verify_kwargs",
    [
        {"times": 0},
        {"between": (0, 2)},
    ],
    ids=["times_0", "between_0_2"],
)
def test_in_order_verify_zero_lower_bound_does_not_fail_on_empty_queue(
    verify_kwargs,
):
    cat = mock()

    in_order: InOrder = InOrder(cat)

    in_order.verify(cat, **verify_kwargs).meow()

    cat.meow()
    in_order.verify(cat).meow()
