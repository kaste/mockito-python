
import pytest

from collections import namedtuple
from functools import partial

from mockito import when, args, kwargs, invocation, mock
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


    @pytest.mark.parametrize('call', [
        sig('Wuff', then='Waff'),
        sig('Wuff', 'Wuff', then='Waff'),
        sig('Wuff', then='Waff', later='Woff'),
        sig('Wuff', first="Wiff", then='Waff', later='Woff'),
        sig('Wuff', 'Wuff', then='Waff', later="Woff"),

        sig().raises(InvocationError),
        sig('Wuff').raises(InvocationError),
        sig('Wuff', 'Wuff').raises(InvocationError),
        sig(later='Woff').raises(InvocationError),
        sig('Wuff', later='Woff').raises(InvocationError),
    ])
    def testCombinedArgsAndKwargs(self, call):
        rex = Dog()
        when(rex).bark('Wuff', *args, then='Waff', **kwargs).thenReturn('Miau')

        assert rex.bark(*call.args, **call.kwargs) == 'Miau'


    @pytest.mark.parametrize('call', [
        sig(Ellipsis),
        sig(Ellipsis, 'Wuff').raises(TypeError),
        sig(Ellipsis, then='Wuff').raises(TypeError),
        sig(Ellipsis, 'Wuff', then='Waff').raises(TypeError),
    ])
    def testEllipsisMustBeLastThing(self, call):
        rex = Dog()
        when(rex).bark(*call.args, **call.kwargs).thenReturn('Miau')


    def testArgsMustUsedAsStarArg(self):
        rex = Dog()
        with pytest.raises(TypeError):
            when(rex).bark(args).thenReturn('Miau')

    def testKwargsMustBeUsedAsStarKwarg(self):
        rex = Dog()
        with pytest.raises(TypeError):
            when(rex).bark(kwargs).thenReturn('Miau')

        with pytest.raises(TypeError):
            when(rex).bark(*kwargs).thenReturn('Miau')

    def testNiceFormattingForEllipsis(self):
        inv = invocation.StubbedInvocation(mock(), 'bark', None)
        inv(Ellipsis)

        assert repr(inv) == 'bark(...)'

    def testNiceFormattingForArgs(self):
        inv = invocation.StubbedInvocation(mock(), 'bark', None)
        inv(*args)

        assert repr(inv) == 'bark(*args)'

    def testNiceFormattingForKwargs(self):
        inv = invocation.StubbedInvocation(mock(), 'bark', None)
        inv(**kwargs)

        assert repr(inv) == 'bark(**kwargs)'

