import pytest

from mockito import expect, mock, ArgumentError, VerificationError
from mockito.inorder import InOrder
from mockito import verify


class Dog:
    def say(self, what):
        return what

    def __str__(self):
        return "<Dog>"


def test_observing_the_same_mock_twice_should_raise():
    a = mock()
    with pytest.raises(ValueError) as e:
        InOrder(a, a)
    assert str(e.value) == ("\nThe following Mocks are duplicated: "
                            f"['{a}']")

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
