import pytest
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


class Action(object):
    def run(self, arg):
        return arg

    def __call__(self, task):
        return task


class TestAction:
    def testA(self):
        when(Action).__call__(Ellipsis).thenReturn('Done')

        action = Action()
        assert action('work') == 'Done'


class TestSpeccing:
    def testA(self):
        action = mock(Action)

        when(action).run(11).thenReturn(12)
        with pytest.raises(Exception):
            when(action).remember()

        assert action.run(11) == 12

    def testB(self):
        action = mock({'foo': 'bar'}, spec=Action)

        assert action.foo == 'bar'
        with pytest.raises(Exception):
            when(action).remember()

