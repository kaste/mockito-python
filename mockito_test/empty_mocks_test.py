
from mockito import mock


class TestEmptyMocks:

    def testAllMethodsReturnNone(self):

        dummy = mock()

        assert dummy.foo() is None
        assert dummy.foo(1, 2) is None


    def testConfigureDummy(self):

        dummy = mock({'foo': 'bar'})

        assert dummy.foo == 'bar'

