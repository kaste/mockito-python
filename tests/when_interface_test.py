
import math
import functools

import pytest

from mockito import (when, when2, expect, verify, patch, mock, spy2,
                     verifyExpectedInteractions)
from mockito.invocation import InvocationError

class Dog(object):
    def bark(self):
        pass


class Cat(object):
    age = 7


class ClassDog(object):
    @classmethod
    def bark(cls):
        pass


class StaticDog(object):
    @staticmethod
    def bark():
        pass


class PartialMethodDog(object):
    def bark(self, sound):
        return sound

    bark_once = functools.partialmethod(bark, 'Wuff')


class _CallableAttribute:
    def __call__(self):
        return "Wuff"


class CallableAttributeDog(object):
    bark = _CallableAttribute()


class DynamicCallableMeta(type):
    def __getattr__(cls, name):
        if name == "bark":
            return lambda: "Wuff"
        raise AttributeError(name)


class DynamicCallableMetaDog(metaclass=DynamicCallableMeta):
    pass


class Unhashable(object):
    def update(self, **kwargs):
        pass

    def __hash__(self):
        raise TypeError("I'm immutable")


@pytest.mark.usefixtures('unstub')
class TestEnsureEmptyInterfacesAreReturned:

    def testWhen(self):
        whening = when(Dog)
        assert whening.__dict__ == {}

    def testExpect(self):
        expecting = expect(Dog)
        assert expecting.__dict__ == {}

    def testVerify(self):
        dummy = mock()
        verifying = verify(dummy)
        assert verifying.__dict__ == {}


def testEnsureUnhashableObjectCanBeMocked():
    obj = Unhashable()
    when(obj).update().thenReturn(None)


class TestAnswerShortcuts:
    def testAssumeReturnNoneIfOmitted(self):
        dog = Dog()
        when(dog).bark().thenReturn().thenReturn(42)
        assert dog.bark() is None
        assert dog.bark() == 42

    def testAssumeReturnNoneIfAnswerIsOmitted(self):
        dog = Dog()
        when(dog).bark().thenAnswer().thenReturn(42)
        assert dog.bark() is None
        assert dog.bark() == 42

    def testAssumeRaiseExceptionIfOmitted(self):
        dog = Dog()
        when(dog).bark().thenRaise().thenReturn(42)
        with pytest.raises(Exception):
            dog.bark()
        assert dog.bark() == 42


@pytest.mark.usefixtures('unstub')
class TestMissingInvocationParentheses:

    def testWhenRaisesEarlyIfMethodCallParenthesesAreMissing(self):
        with pytest.raises(InvocationError) as exc:
            when(Dog).bark.thenReturn('Sure')

        assert str(exc.value) == "expected an invocation of 'bark'"

    def testExpectRaisesEarlyIfMethodCallParenthesesAreMissing(self):
        with pytest.raises(InvocationError) as exc:
            expect(Dog).bark.thenReturn('Sure')

        assert str(exc.value) == "expected an invocation of 'bark'"

    def testWhenRaisesEarlyForThenRaiseIfMethodCallParenthesesAreMissing(self):
        with pytest.raises(InvocationError) as exc:
            when(Dog).bark.thenRaise(RuntimeError('Boom'))

        assert str(exc.value) == "expected an invocation of 'bark'"

    def testExpectRaisesEarlyForThenRaiseIfMethodCallParenthesesAreMissing(self):
        with pytest.raises(InvocationError) as exc:
            expect(Dog).bark.thenRaise(RuntimeError('Boom'))

        assert str(exc.value) == "expected an invocation of 'bark'"

    def testWhenRaisesEarlyForThenAnswerIfMethodCallParenthesesAreMissing(self):
        with pytest.raises(InvocationError) as exc:
            when(Dog).bark.thenAnswer(lambda: 'Sure')

        assert str(exc.value) == "expected an invocation of 'bark'"

    def testExpectRaisesEarlyForThenAnswerIfMethodCallParenthesesAreMissing(self):
        with pytest.raises(InvocationError) as exc:
            expect(Dog).bark.thenAnswer(lambda: 'Sure')

        assert str(exc.value) == "expected an invocation of 'bark'"

    def testWhenRaisesEarlyForThenCallOriginalIfMethodCallParenthesesAreMissing(self):
        with pytest.raises(InvocationError) as exc:
            when(Dog).bark.thenCallOriginalImplementation()

        assert str(exc.value) == "expected an invocation of 'bark'"

    def testExpectRaisesEarlyForThenCallOriginalIfMethodCallParenthesesAreMissing(self):
        with pytest.raises(InvocationError) as exc:
            expect(Dog).bark.thenCallOriginalImplementation()

        assert str(exc.value) == "expected an invocation of 'bark'"

    def testWhenRaisesEarlyForClassmethodIfParenthesesAreMissing(self):
        with pytest.raises(InvocationError) as exc:
            when(ClassDog).bark.thenReturn('Sure')

        assert str(exc.value) == "expected an invocation of 'bark'"

    def testExpectRaisesEarlyForClassmethodIfParenthesesAreMissing(self):
        with pytest.raises(InvocationError) as exc:
            expect(ClassDog).bark.thenReturn('Sure')

        assert str(exc.value) == "expected an invocation of 'bark'"

    def testWhenRaisesEarlyForStaticmethodIfParenthesesAreMissing(self):
        with pytest.raises(InvocationError) as exc:
            when(StaticDog).bark.thenReturn('Sure')

        assert str(exc.value) == "expected an invocation of 'bark'"

    def testExpectRaisesEarlyForStaticmethodIfParenthesesAreMissing(self):
        with pytest.raises(InvocationError) as exc:
            expect(StaticDog).bark.thenReturn('Sure')

        assert str(exc.value) == "expected an invocation of 'bark'"

    def testWhenRaisesEarlyForBuiltinFunctionIfParenthesesAreMissing(self):
        with pytest.raises(InvocationError) as exc:
            when(math).sin.thenReturn(0)

        assert str(exc.value) == "expected an invocation of 'sin'"

    def testExpectRaisesEarlyForBuiltinFunctionIfParenthesesAreMissing(self):
        with pytest.raises(InvocationError) as exc:
            expect(math).sin.thenReturn(0)

        assert str(exc.value) == "expected an invocation of 'sin'"

    def testWhenRaisesEarlyForBuiltinMethodDescriptorIfMissing(self):
        with pytest.raises(InvocationError) as exc:
            when(dict).get.thenReturn('Sure')

        assert str(exc.value) == "expected an invocation of 'get'"

    def testWhenRaisesEarlyForBuiltinWrapperDescriptorIfParenthesesAreMissing(self):
        with pytest.raises(InvocationError) as exc:
            when(str).__len__.thenReturn(1)

        assert str(exc.value) == "expected an invocation of '__len__'"

    def testWhenRaisesEarlyForBuiltinClassMethodDescriptorIfParenthesesAreMissing(self):
        with pytest.raises(InvocationError) as exc:
            when(dict).fromkeys.thenReturn({})

        assert str(exc.value) == "expected an invocation of 'fromkeys'"

    def testExpectRaisesEarlyForBuiltinMethodDescriptorIfMissing(self):
        with pytest.raises(InvocationError) as exc:
            expect(dict).get.thenReturn('Sure')

        assert str(exc.value) == "expected an invocation of 'get'"

    def testWhenRaisesEarlyForPartialmethodIfParenthesesAreMissing(self):
        with pytest.raises(InvocationError) as exc:
            when(PartialMethodDog).bark_once.thenReturn('Sure')

        assert str(exc.value) == "expected an invocation of 'bark_once'"

    def testWhenRaisesEarlyForCallableAttributeIfParenthesesAreMissing(self):
        with pytest.raises(InvocationError) as exc:
            when(CallableAttributeDog).bark.thenReturn('Sure')

        assert str(exc.value) == "expected an invocation of 'bark'"

    def testWhenRaisesEarlyForDynamicMetaclassCallableIfParenthesesAreMissing(self):
        with pytest.raises(InvocationError) as exc:
            when(DynamicCallableMetaDog).bark.thenReturn('Sure')

        assert str(exc.value) == "expected an invocation of 'bark'"


@pytest.mark.usefixtures('unstub')
class TestPassAroundStrictness:

    def testReconfigureStrictMock(self):
        when(Dog).bark()  # important first call, inits theMock

        when(Dog, strict=False).waggle().thenReturn('Sure')
        expect(Dog, strict=False).weggle().thenReturn('Sure')


        with pytest.raises(InvocationError):
            when(Dog).wuggle()

        with pytest.raises(InvocationError):
            when(Dog).woggle()

        rex = Dog()
        assert rex.waggle() == 'Sure'
        assert rex.weggle() == 'Sure'

        # For documentation; the initial strict value of the mock will be used
        # here. So the above when(..., strict=False) just assures we can
        # actually *add* an attribute to the mocked object
        with pytest.raises(InvocationError):
            rex.waggle(1)

        verify(Dog).waggle()
        verify(Dog).weggle()

    def testReconfigureLooseMock(self):
        when(Dog, strict=False).bark()  # important first call, inits theMock

        when(Dog, strict=False).waggle().thenReturn('Sure')
        expect(Dog, strict=False).weggle().thenReturn('Sure')

        with pytest.raises(InvocationError):
            when(Dog).wuggle()

        with pytest.raises(InvocationError):
            when(Dog).woggle()

        rex = Dog()
        assert rex.waggle() == 'Sure'
        assert rex.weggle() == 'Sure'

        # For documentation; see test above. strict is inherited from the
        # initial mock. So we return `None`
        assert rex.waggle(1) is None

        verify(Dog).waggle()
        verify(Dog).weggle()


class TestEnsureAddedAttributesGetRemovedOnUnstub:
    def testWhenPatchingTheClass(self):
        with when(Dog, strict=False).wggle():
            Dog().wggle()

        with pytest.raises(AttributeError):
            Dog.wggle

    def testWhenPatchingAnInstance(self):
        dog = Dog()
        with when(dog, strict=False).wggle():
            dog.wggle()

        with pytest.raises(AttributeError):
            dog.wggle


@pytest.mark.usefixtures('unstub')
class TestNonCallableAttributesCannotBeStubbedAsMethods:
    def testExpectRaisesEarlyIfAttributeIsNotCallable(self):
        with pytest.raises(InvocationError) as exc:
            expect(Cat).age()
        assert str(exc.value) == "'age' is not callable."

    def testWhenStrictFalseRaisesEarlyIfAttributeIsNotCallable(self):
        with pytest.raises(InvocationError) as exc:
            when(Cat, strict=False).age()
        assert str(exc.value) == "'age' is not callable."

@pytest.mark.usefixtures('unstub')
class TestDottedPaths:

    def testWhen(self):
        when('os.path').exists('/Foo').thenReturn(True)

        import os.path
        assert os.path.exists('/Foo')

    def testWhen2(self):
        when2('os.path.exists', '/Foo').thenReturn(True)

        import os.path
        assert os.path.exists('/Foo')

    def testExpect(self):
        expect('os.path', times=2).exists('/Foo').thenReturn(True)

        import os.path
        os.path.exists('/Foo')
        assert os.path.exists('/Foo')
        verifyExpectedInteractions()

    def testPatch(self):
        dummy = mock()
        patch('os.path.exists', dummy)

        import os.path
        assert os.path.exists('/Foo') is None

        verify(dummy).__call__('/Foo')

    def testVerify(self):
        when('os.path').exists('/Foo').thenReturn(True)

        import os.path
        os.path.exists('/Foo')

        verify('os.path', times=1).exists('/Foo')

    def testSpy2(self):
        spy2('os.path.exists')

        import os.path
        assert not os.path.exists('/Foo')

        verify('os.path', times=1).exists('/Foo')
