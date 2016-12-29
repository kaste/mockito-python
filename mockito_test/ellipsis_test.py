
import pytest

from collections import namedtuple
from functools import partial

from mockito import when, args, kwargs
from mockito.invocation import InvocationError


class Dog(object):
    def bark(self, sound):
        return "%s!" % sound


class CallSignature(namedtuple('CallSignature', 'args kwargs')):
    def raises(self, reason):
        return pytest.mark.xfail(self, raises=reason, strict=True)

def sig(*args, **kwargs):
    return CallSignature(args, kwargs)


expect = partial(pytest.mark.xfail, strict=True)


class TestEllipsises:

    # In python3 `bark(...)` is actually valid, but the tests must
    # be downwards compatible to python 2

    @pytest.mark.parametrize('call', [
        sig(),
        sig('Wuff'),
        sig('Wuff', 'Wuff'),
        sig('Wuff', then='Wuff'),
        sig(then='Wuff'),
    ])
    def testEllipsisAsSoleArgument(self, call):
        rex = Dog()
        when(rex).bark(Ellipsis).thenReturn('Miau')

        assert rex.bark(*call.args, **call.kwargs) == 'Miau'


    @pytest.mark.parametrize('call', [
        sig().raises(InvocationError),
        sig('Wuff'),
        sig('Wuff', 'Wuff'),
        sig('Wuff', then='Wuff'),
        sig(then='Wuff').raises(InvocationError),
    ])
    def testEllipsisAsSecondArgument(self, call):
        rex = Dog()
        when(rex).bark('Wuff', Ellipsis).thenReturn('Miau')

        assert rex.bark(*call.args, **call.kwargs) == 'Miau'


    @pytest.mark.parametrize('call', [
        sig(),
        sig('Wuff'),
        sig('Wuff', 'Wuff'),
        sig('Wuff', then='Wuff').raises(InvocationError),
        sig(then='Wuff').raises(InvocationError),
    ])
    def testArgsAsSoleArgument(self, call):
        rex = Dog()
        when(rex).bark(*args).thenReturn('Miau')

        assert rex.bark(*call.args, **call.kwargs) == 'Miau'


    @pytest.mark.parametrize('call', [
        sig().raises(InvocationError),
        sig('Wuff'),
        sig('Wuff', 'Wuff'),
        sig('Wuff', then='Wuff').raises(InvocationError),
        sig(then='Wuff').raises(InvocationError),
    ])
    def testArgsAsSecondArgument(self, call):
        rex = Dog()
        when(rex).bark('Wuff', *args).thenReturn('Miau')

        assert rex.bark(*call.args, **call.kwargs) == 'Miau'


    @pytest.mark.parametrize('call', [
        sig().raises(InvocationError),
        sig('Wuff').raises(InvocationError),
        sig('Wuff', 'Wuff').raises(InvocationError),
        sig('Wuff', then='Wuff'),
        sig('Wuff', 'Wuff', then='Wuff'),
        sig(then='Wuff').raises(InvocationError),

    ])
    def testArgsBeforeConcreteKwarg(self, call):
        rex = Dog()
        when(rex).bark('Wuff', *args, then='Wuff').thenReturn('Miau')

        assert rex.bark(*call.args, **call.kwargs) == 'Miau'


    @pytest.mark.parametrize('call', [
        sig(),
        sig('Wuff').raises(InvocationError),
        sig('Wuff', 'Wuff').raises(InvocationError),
        sig('Wuff', then='Wuff').raises(InvocationError),
        sig('Wuff', 'Wuff', then='Wuff').raises(InvocationError),
        sig(then='Wuff'),
        sig(then='Wuff', later='Waff')

    ])
    def testKwargsAsSoleArgument(self, call):
        rex = Dog()
        when(rex).bark(**kwargs).thenReturn('Miau')

        assert rex.bark(*call.args, **call.kwargs) == 'Miau'


    @pytest.mark.parametrize('call', [
        sig().raises(InvocationError),
        sig('Wuff').raises(InvocationError),
        sig('Wuff', 'Wuff').raises(InvocationError),
        sig('Wuff', then='Wuff').raises(InvocationError),
        sig('Wuff', 'Wuff', then='Wuff').raises(InvocationError),
        sig(then='Wuff'),
        sig(then='Wuff', later='Waff'),
        sig(later='Waff', then='Wuff'),
        sig(first='Wuff', later='Waff').raises(InvocationError)

    ])
    def testKwargsAsSecondKwarg(self, call):
        rex = Dog()
        when(rex).bark(then='Wuff', **kwargs).thenReturn('Miau')

        assert rex.bark(*call.args, **call.kwargs) == 'Miau'
        # 1/0


    # implementation detail: See MatchingInvocation.matches
    def testEnsureKwargsSentinelIsAtTheEnd(self):
        from mockito.matchers import KWARGS_SENTINEL

        d = {'a': 1, KWARGS_SENTINEL: 3, 'Z': 2}
        d_ = sorted(d.items(), reverse=True)
        assert d_[-1][0] is KWARGS_SENTINEL

