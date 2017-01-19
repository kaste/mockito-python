
from mockito import when, expect, verify


class Dog(object):
    def remember(self):
        pass


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
