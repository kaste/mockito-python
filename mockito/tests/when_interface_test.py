
from mockito import when, expect, verify


class Dog(object):
    def remember(self):
        pass


class Unhashable(object):
    def update(self, **kwargs):
        pass

    def __hash__(self):
        raise TypeError("I'm immutable")


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

