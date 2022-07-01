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


class _QueryProperty:
    def __get__(self, obj, type):
        assert obj is None, "query is a class property"
        return 42

class Base():
    query = _QueryProperty()

class User(Base):
    pass

def test_sqlalchemy_1(monkeypatch):
    assert User.query == 42
    query_prop = mock()
    when(query_prop).filter_by(...).thenReturn(
        mock({"first": lambda: "A user"})
    )

    monkeypatch.setattr(User, "query", query_prop)
    assert User.query.filter_by(username='admin').first() == "A user"

def test_sqlalchemy_2():
    assert User.query == 42
    query_prop = mock()
    when(query_prop).filter_by(...).thenReturn(
        mock({"first": lambda: "A user"})
    )
    with when(_QueryProperty).__get__(...).thenReturn(query_prop):
        assert User.query.filter_by(username='admin').first() == "A user"

@pytest.mark.xfail(reason='Not implemented.')
def test_sqlalchemy_3a():
    assert User.query == 42
    query_prop = mock()
    when(query_prop).filter_by(...).first().thenReturn("A user")
    with when(_QueryProperty).__get__(...).thenReturn(query_prop):
        assert User.query.filter_by(username='admin').first() == "A user"

@pytest.mark.xfail(reason='Not implemented.')
def test_sqlalchemy_3b(unstub):  # atm throws badly, ensure unstub manually
    assert User.query == 42
    with when(User).query.filter_by(...).first().thenReturn("A user"):
        assert User.query.filter_by(username='admin').first() == "A user"

def test_sqlalchemy_4_ensure_unstubbed():
    assert User.query == 42
