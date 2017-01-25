
import pytest

from mockito import when, expect, verify, mock
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


class TestPassAroundStrictness:

    def testA(self):
        when(Dog).bark()  # important first call, inits theMock

        when(Dog, strict=False).waggle()
        expect(Dog, strict=False).weggle()

        with pytest.raises(InvocationError):
            when(Dog).wuggle()

        with pytest.raises(InvocationError):
            when(Dog).woggle()


