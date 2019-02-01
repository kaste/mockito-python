import pytest
from mockito import mock, when

def test_deprecated_a(unstub):
    # Setting on `__class__` is confusing for users
    m = mock()

    prop = mock()
    when(prop).__get__(Ellipsis).thenRaise(ValueError)
    m.__class__.tx = prop

    with pytest.raises(ValueError):
        m.tx


def test_deprecated_b(unstub):
    # Setting on `__class__` is confusing for users
    m = mock()

    def _raise(*a):
        print(a)
        raise ValueError('Boom')

    m.__class__.tx = property(_raise)

    with pytest.raises(ValueError):
        m.tx


def test_deprecated_c(unstub):
    # Setting on `__class__` is confusing for users
    # Wrapping explicitly with `property` as well
    m = mock()

    prop = mock(strict=True)
    when(prop).__call__(Ellipsis).thenRaise(ValueError)
    m.__class__.tx = property(prop)

    with pytest.raises(ValueError):
        m.tx


def test_recommended_approach():
    prop = mock(strict=True)
    when(prop).__get__(Ellipsis).thenRaise(ValueError)

    m = mock({'tx': prop})
    with pytest.raises(ValueError):
        m.tx
