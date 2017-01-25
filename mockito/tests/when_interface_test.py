
import pytest

from mockito import when, expect, verify
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
class TestUserExposedInterfaces:

    def testWhen(self):
        whening = when(Dog)
        assert whening.__dict__ == {}

    def testExpect(self):
        expecting = expect(Dog)
        assert expecting.__dict__ == {}

    def testVerify(self):
        verifying = verify(Dog)
        assert verifying.__dict__ == {}


    def testEnsureUnhashableObjectCanBeMocked(self):
        obj = Unhashable()
        when(obj).update().thenReturn(None)


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

        # For documentation; the inital strict value of the mock will be used
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


