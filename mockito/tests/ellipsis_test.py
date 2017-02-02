
import pytest

from collections import namedtuple

from mockito import when, args, kwargs, invocation, mock


class Dog(object):
    def bark(self, sound):
        return "%s!" % sound


class CallSignature(namedtuple('CallSignature', 'args kwargs')):
    def raises(self, reason):
        return pytest.mark.xfail(self, raises=reason, strict=True)

def sig(*args, **kwargs):
    return CallSignature(args, kwargs)



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
    def testEllipsisAsSoleArgumentAlwaysPasses(self, call):
        rex = mock()
        when(rex).bark(Ellipsis).thenReturn('Miau')

        assert rex.bark(*call.args, **call.kwargs) == 'Miau'


    @pytest.mark.parametrize('call', [
        sig('Wuff'),
        sig('Wuff', 'Wuff'),
        sig('Wuff', then='Wuff'),
    ])
    def testEllipsisAsSecondArgumentPasses(self, call):
        rex = mock()
        when(rex).bark('Wuff', Ellipsis).thenReturn('Miau')

        assert rex.bark(*call.args, **call.kwargs) == 'Miau'

    @pytest.mark.parametrize('call', [
        sig(),
        sig(then='Wuff'),
    ])
    def testEllipsisAsSecondArgumentRejections(self, call):
        rex = mock()
        when(rex).bark('Wuff', Ellipsis).thenReturn('Miau')

        with pytest.raises(AssertionError):
            assert rex.bark(*call.args, **call.kwargs) == 'Miau'


    @pytest.mark.parametrize('call', [
        sig(),
        sig('Wuff'),
        sig('Wuff', 'Wuff'),
    ])
    def testArgsAsSoleArgumentPasses(self, call):
        rex = mock()
        when(rex).bark(*args).thenReturn('Miau')

        assert rex.bark(*call.args, **call.kwargs) == 'Miau'

    @pytest.mark.parametrize('call', [
        sig('Wuff', then='Wuff'),
        sig(then='Wuff'),
    ])
    def testArgsAsSoleArgumentRejections(self, call):
        rex = mock()
        when(rex).bark(*args).thenReturn('Miau')

        with pytest.raises(AssertionError):
            assert rex.bark(*call.args, **call.kwargs) == 'Miau'


    @pytest.mark.parametrize('call', [
        sig('Wuff'),
        sig('Wuff', 'Wuff'),
    ])
    def testArgsAsSecondArgumentPasses(self, call):
        rex = mock()
        when(rex).bark('Wuff', *args).thenReturn('Miau')

        assert rex.bark(*call.args, **call.kwargs) == 'Miau'

    @pytest.mark.parametrize('call', [
        sig(),
        sig('Wuff', then='Wuff'),
        sig(then='Wuff'),
    ])
    def testArgsAsSecondArgumentRejections(self, call):
        rex = mock()
        when(rex).bark('Wuff', *args).thenReturn('Miau')

        with pytest.raises(AssertionError):
            assert rex.bark(*call.args, **call.kwargs) == 'Miau'


    @pytest.mark.parametrize('call', [
        sig('Wuff', then='Wuff'),
        sig('Wuff', 'Wuff', then='Wuff'),

    ])
    def testArgsBeforeConcreteKwargPasses(self, call):
        rex = mock()
        when(rex).bark('Wuff', *args, then='Wuff').thenReturn('Miau')

        assert rex.bark(*call.args, **call.kwargs) == 'Miau'

    @pytest.mark.parametrize('call', [
        sig(),
        sig('Wuff'),
        sig('Wuff', 'Wuff'),
        sig(then='Wuff'),

    ])
    def testArgsBeforeConcreteKwargRejections(self, call):
        rex = mock()
        when(rex).bark('Wuff', *args, then='Wuff').thenReturn('Miau')

        with pytest.raises(AssertionError):
            assert rex.bark(*call.args, **call.kwargs) == 'Miau'


    @pytest.mark.parametrize('call', [
        sig(),
        sig(then='Wuff'),
        sig(then='Wuff', later='Waff')
    ])
    def testKwargsAsSoleArgumentPasses(self, call):
        rex = mock()
        when(rex).bark(**kwargs).thenReturn('Miau')

        assert rex.bark(*call.args, **call.kwargs) == 'Miau'

    @pytest.mark.parametrize('call', [
        sig('Wuff'),
        sig('Wuff', 'Wuff'),
        sig('Wuff', then='Wuff'),
        sig('Wuff', 'Wuff', then='Wuff'),
    ])
    def testKwargsAsSoleArgumentRejections(self, call):
        rex = mock()
        when(rex).bark(**kwargs).thenReturn('Miau')

        with pytest.raises(AssertionError):
            assert rex.bark(*call.args, **call.kwargs) == 'Miau'


    @pytest.mark.parametrize('call', [
        sig(then='Wuff'),
        sig(then='Wuff', later='Waff'),
        sig(later='Waff', then='Wuff'),
    ])
    def testKwargsAsSecondKwargPasses(self, call):
        rex = mock()
        when(rex).bark(then='Wuff', **kwargs).thenReturn('Miau')

        assert rex.bark(*call.args, **call.kwargs) == 'Miau'

    @pytest.mark.parametrize('call', [
        sig(),
        sig('Wuff'),
        sig('Wuff', 'Wuff'),
        sig('Wuff', then='Wuff'),
        sig('Wuff', 'Wuff', then='Wuff'),
        sig(first='Wuff', later='Waff')
    ])
    def testKwargsAsSecondKwargRejections(self, call):
        rex = mock()
        when(rex).bark(then='Wuff', **kwargs).thenReturn('Miau')

        with pytest.raises(AssertionError):
            assert rex.bark(*call.args, **call.kwargs) == 'Miau'


    @pytest.mark.parametrize('call', [
        sig('Wuff', then='Waff'),
        sig('Wuff', 'Wuff', then='Waff'),
        sig('Wuff', then='Waff', later='Woff'),
        sig('Wuff', first="Wiff", then='Waff', later='Woff'),
        sig('Wuff', 'Wuff', then='Waff', later="Woff"),
    ])
    def testCombinedArgsAndKwargsPasses(self, call):
        rex = mock()
        when(rex).bark('Wuff', *args, then='Waff', **kwargs).thenReturn('Miau')

        assert rex.bark(*call.args, **call.kwargs) == 'Miau'

    @pytest.mark.parametrize('call', [
        sig(),
        sig('Wuff'),
        sig('Wuff', 'Wuff'),
        sig(later='Woff'),
        sig('Wuff', later='Woff'),
    ])
    def testCombinedArgsAndKwargsRejections(self, call):
        rex = mock()
        when(rex).bark('Wuff', *args, then='Waff', **kwargs).thenReturn('Miau')

        with pytest.raises(AssertionError):
            assert rex.bark(*call.args, **call.kwargs) == 'Miau'


    @pytest.mark.parametrize('call', [
        sig(Ellipsis),
    ])
    def testEllipsisMustBeLastThing(self, call):
        rex = mock()
        when(rex).bark(*call.args, **call.kwargs).thenReturn('Miau')

    @pytest.mark.parametrize('call', [
        sig(Ellipsis, 'Wuff'),
        sig(Ellipsis, then='Wuff'),
        sig(Ellipsis, 'Wuff', then='Waff'),
    ])
    def testEllipsisMustBeLastThingRejections(self, call):
        rex = mock()
        with pytest.raises(TypeError):
            when(rex).bark(*call.args, **call.kwargs).thenReturn('Miau')


    def testArgsMustUsedAsStarArg(self):
        rex = mock()
        with pytest.raises(TypeError):
            when(rex).bark(args).thenReturn('Miau')

    def testKwargsMustBeUsedAsStarKwarg(self):
        rex = mock()
        with pytest.raises(TypeError):
            when(rex).bark(kwargs).thenReturn('Miau')

        with pytest.raises(TypeError):
            when(rex).bark(*kwargs).thenReturn('Miau')

    def testNiceFormattingForEllipsis(self):
        m = mock()
        m.strict = False
        inv = invocation.StubbedInvocation(m, 'bark', None)
        inv(Ellipsis)

        assert repr(inv) == 'bark(...)'

    def testNiceFormattingForArgs(self):
        m = mock()
        m.strict = False
        inv = invocation.StubbedInvocation(m, 'bark', None)
        inv(*args)

        assert repr(inv) == 'bark(*args)'

    def testNiceFormattingForKwargs(self):
        m = mock()
        m.strict = False
        inv = invocation.StubbedInvocation(m, 'bark', None)
        inv(**kwargs)

        assert repr(inv) == 'bark(**kwargs)'

