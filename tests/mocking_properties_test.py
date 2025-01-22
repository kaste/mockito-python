import pytest
from mockito import mock, verify, when
from mockito.invocation import return_

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


def test_recommended_approach_1(unstub):
    prop = mock()
    when(prop).__get__(Ellipsis).thenRaise(ValueError)

    m = mock({'tx': prop})
    with pytest.raises(ValueError):
        m.tx
    verify(prop).__get__(...)


def test_recommended_approach_2(unstub):
    prop = mock()
    when(prop).__get__(Ellipsis).thenReturn(42)

    m = mock({'tx': prop})
    assert m.tx == 42
    verify(prop).__get__(...)


def test_recommended_approach_3(unstub):
    prop = mock({"__get__": return_(42)})
    m = mock({'tx': prop})
    assert m.tx == 42
    verify(prop).__get__(...)


def test_recommended_approach_4(unstub):
    # Elegant but you can't `verify` the usage explicitly
    # which makes it moot -- why not just set `m.tx = 42` then?
    m = mock({'tx': property(return_(42))})
    assert m.tx == 42
