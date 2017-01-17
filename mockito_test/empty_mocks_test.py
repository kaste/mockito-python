
from mockito import mock, verify, when


class TestEmptyMocks:

    def testAllMethodsReturnNone(self):

        dummy = mock()

        assert dummy.foo() is None
        assert dummy.foo(1, 2) is None


    def testConfigureDummy(self):
        dummy = mock({'foo': 'bar'})
        assert dummy.foo == 'bar'


    def testDummiesAreCallable(self):
        dummy = mock()
        assert dummy() is None
        assert dummy(1, 2) is None


    def testCallsAreVerifiable(self):
        dummy = mock()
        dummy(1, 2)

        verify(dummy).__call__(1, 2)

