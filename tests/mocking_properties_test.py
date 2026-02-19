import pytest
from mockito import mock, verify, when, unstub as unstub_all, invocation
from mockito.invocation import InvocationError, return_


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


# The following "recommended" approaches are what we had before
# we got first class property support.  It is the recommended
# approach within the old framework.
# The new behavior starts below with "class F".


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
    with when(User).query.thenReturn(query_prop):
        assert User.query.filter_by(username='admin').first() == "A user"

@pytest.mark.xfail(reason='Not implemented.')
def test_sqlalchemy_3a():
    assert User.query == 42
    query_prop = mock()
    when(query_prop).filter_by(...).first().thenReturn("A user")
    with when(User).query.thenReturn(query_prop):
        assert User.query.filter_by(username='admin').first() == "A user"

@pytest.mark.xfail(reason='Not implemented.')
def test_sqlalchemy_3b(unstub):  # atm throws badly, ensure unstub manually
    assert User.query == 42
    with when(User).query.filter_by(...).first().thenReturn("A user"):
        assert User.query.filter_by(username='admin').first() == "A user"

def test_sqlalchemy_4_ensure_unstubbed():
    assert User.query == 42


class F:
    query = _QueryProperty()

    @property
    def p(self):
        return 42


def test_property_access():
    assert F().p == 42
    with when(F).p.thenReturn(23):
        assert F().p == 23
    assert F().p == 42

    with pytest.raises(invocation.InvocationError):
        when(F).fool.thenReturn(23)
    with pytest.raises(AttributeError):
        assert F().fool == 23  # type: ignore[attr-defined]


def test_invalid_property_stubbing_does_not_change_property_behavior(unstub):
    assert F().p == 42

    with pytest.raises(AttributeError) as exc:
        with when(F).p.thenRtu(12):
            pass

    assert str(exc.value) == (
        "Unknown stubbing action 'thenRtu'. "
        "Use one of: thenReturn, thenRaise, thenAnswer, "
        "thenCallOriginalImplementation."
    )
    assert F().p == 42


def test_hasattr_on_when_property_access_does_not_patch_target(unstub):
    assert F().p == 42

    assert not hasattr(when(F).p, 'unknown_attribute')

    assert F().p == 42


def test_missing_parentheses_on_property_selector_does_not_patch_target(unstub):
    assert F().p == 42

    # Python versions differ here (`TypeError` vs `AttributeError('__enter__')`).
    with pytest.raises((TypeError, AttributeError)):
        with when(F).p.thenReturn:
            pass

    assert F().p == 42


def test_property_access_then_return_then_call_original_implementation():
    assert F().p == 42

    with when(F).p.thenReturn(21).thenCallOriginalImplementation():
        assert F().p == 21
        assert F().p == 42
        assert F().p == 42

    assert F().p == 42


def test_descriptor_access():
    assert F.query == 42
    with when(F).query.thenReturn(23):
        assert F.query == 23
    assert F.query == 42

def test_failed_instance_property_stubbing_does_not_poison_unstub():
    f = F()
    assert f.p == 42

    with pytest.raises(InvocationError):
        when(f).p.thenReturn(23)

    assert f.p == 42
    unstub_all()
    assert f.p == 42


def test_instance_property_stubbing_fails_fast_with_guidance(unstub):
    f = F()

    with pytest.raises(InvocationError) as exc:
        when(f).p.thenReturn(23)

    assert str(exc.value) == (
        "Cannot stub property 'p' on an instance. "
        "Use class-level stubbing instead: when(F).p.thenReturn(...)."
    )


class _InstancePropertyWithSideEffects:
    def __init__(self):
        self.getter_calls = 0

    @property
    def p(self):
        self.getter_calls += 1
        return 42


def test_instance_property_stubbing_does_not_execute_getter(unstub):
    f = _InstancePropertyWithSideEffects()

    with pytest.raises(InvocationError):
        when(f).p.thenReturn(23)

    assert f.getter_calls == 0


class _ClassAccessRaisingDescriptor:
    def __get__(self, obj, owner):
        if obj is None:
            raise RuntimeError("descriptor should not run during stubbing")
        return 42


class _ClassAccessRaisingDescriptorUser:
    token = _ClassAccessRaisingDescriptor()


def test_class_descriptor_raising_on_class_access_can_be_stubbed():
    with pytest.raises(RuntimeError):
        _ClassAccessRaisingDescriptorUser.token

    with when(_ClassAccessRaisingDescriptorUser).token.thenReturn(23):
        assert _ClassAccessRaisingDescriptorUser.token == 23

    with pytest.raises(RuntimeError):
        _ClassAccessRaisingDescriptorUser.token


class NestedPropertyAccess:
    @property
    def q(self):
        return 40

    @property
    def p(self):
        return self.q + 2


def test_nested_property_access_then_call_original_implementation():
    nested = NestedPropertyAccess()

    with when(NestedPropertyAccess).p.thenCallOriginalImplementation():
        with when(NestedPropertyAccess).q.thenCallOriginalImplementation():
            assert nested.p == 42
            assert nested.q == 40
            assert nested.p == 42


class ReentrantSamePropertyAccess:
    def __init__(self):
        self._depth = 0

    @property
    def p(self):
        if self._depth == 0:
            self._depth += 1
            try:
                return self.p + 1
            finally:
                self._depth -= 1
        return 41


def test_reentrant_same_property_then_call_original_implementation():
    reentrant = ReentrantSamePropertyAccess()

    with when(ReentrantSamePropertyAccess).p.thenCallOriginalImplementation():
        assert reentrant.p == 42
        assert reentrant.p == 42


def test_property_stubbing_restores_falsy_direct_class_attribute():
    class FalsyDirectClassAttribute:
        token = 0

    assert FalsyDirectClassAttribute.token == 0

    with when(FalsyDirectClassAttribute).token.thenReturn(23):
        assert FalsyDirectClassAttribute.token == 23

    assert FalsyDirectClassAttribute.token == 0


class NonDescriptorAttribute:
    token = 0


def test_property_call_original_missing_implementation_error_message():
    with pytest.raises(invocation.AnswerError) as exc:
        when(NonDescriptorAttribute).token.thenCallOriginalImplementation()

    assert str(exc.value) == (
        "'%s' has no original implementation for '%s'." %
        (NonDescriptorAttribute, 'token')
    )


class _CallableDescriptor:
    def __get__(self, obj, type):
        assert obj is None, "callable descriptor is a class property"
        return lambda: "A user"


class CallableDescriptorUser:
    query = _CallableDescriptor()


def test_callable_descriptor_access_can_be_stubbed():
    assert CallableDescriptorUser.query() == "A user"

    with when(CallableDescriptorUser).query.thenReturn(
        lambda: "Stubbed user"
    ):
        assert CallableDescriptorUser.query() == "Stubbed user"


class _CallableDescriptorObject:
    def __get__(self, obj, type):
        assert obj is None, "callable descriptor object is a class property"
        return "A user"

    def __call__(self):
        return "descriptor object is callable too"


class CallableDescriptorObjectUser:
    query = _CallableDescriptorObject()


def test_callable_descriptor_object_access_can_be_stubbed():
    assert CallableDescriptorObjectUser.query == "A user"

    with when(CallableDescriptorObjectUser).query.thenReturn("Stubbed user"):
        assert CallableDescriptorObjectUser.query == "Stubbed user"


class _InheritedDescriptor:
    def __get__(self, obj, owner):
        return 7 if obj else 42


class _InheritedDescriptorBase:
    token = _InheritedDescriptor()


class _InheritedDescriptorChild(_InheritedDescriptorBase):
    pass


def test_inherited_descriptor_then_call_original_implementation():
    assert _InheritedDescriptorChild.token == 42
    assert _InheritedDescriptorChild().token == 7

    with when(
        _InheritedDescriptorChild
    ).token.thenCallOriginalImplementation():
        assert _InheritedDescriptorChild.token == 42
        assert _InheritedDescriptorChild().token == 7
