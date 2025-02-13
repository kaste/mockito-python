
import pytest

from mockito import (when, when2, expect, verify, patch, mock, spy2,
                     verifyNoUnwantedInteractions)
from mockito.invocation import InvocationError

class Dog(object):
    def bark(self):
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

    def testRaiseIfAnswerIsOmitted(self):
        dog = Dog()
        with pytest.raises(TypeError) as exc:
            when(dog).bark().thenAnswer()
        assert str(exc.value) == "No answer function provided"

    def testAssumeRaiseExceptionIfOmitted(self):
        dog = Dog()
        when(dog).bark().thenRaise().thenReturn(42)
        with pytest.raises(Exception):
            dog.bark()
        assert dog.bark() == 42


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
            pass

        with pytest.raises(AttributeError):
            Dog.wggle

    def testWhenPatchingAnInstance(self):
        dog = Dog()
        with when(dog, strict=False).wggle():
            pass

        with pytest.raises(AttributeError):
            dog.wggle


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
        verifyNoUnwantedInteractions()

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
