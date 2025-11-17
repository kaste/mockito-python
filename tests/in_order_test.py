import pytest

from mockito import mock, VerificationError
from mockito.inorder import InOrder
from mockito import verify

def test_observing_the_same_mock_twice_should_raise():
    a = mock()
    with pytest.raises(ValueError) as e:
        InOrder(a, a)
    assert str(e.value) == ("The following Mocks are duplicated: "
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
    # assert str(e.value) == (
    #     "InOrder verification error! "
    #     f"Wanted a call from {cat}, but got "
    #     f"bark() from {dog} instead!"
    # )


def test_verifing_not_observed_mocks_should_raise():
    cat = mock()
    to_ignore = mock()

    in_order: InOrder = InOrder(cat)
    to_ignore.bark()

    with pytest.raises(VerificationError) as e:
        in_order.verify(to_ignore).bark()
    assert str(e.value) == (
        f"InOrder Verification Error! "
        f"Unexpected call from not observed {to_ignore.mocked_obj}."
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
