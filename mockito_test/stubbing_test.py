#  Copyright (c) 2008-2016 Szczepan Faber, Serhiy Oplakanets, Herr Kaste
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#  THE SOFTWARE.

from mockito_test.test_base import *
from mockito import mock, when, verify, times, any


class StubbingTest(TestBase):
    def testStubsWithReturnValue(self):
        theMock = mock()
        when(theMock).getStuff().thenReturn("foo")
        when(theMock).getMoreStuff(1, 2).thenReturn(10)

        self.assertEquals("foo", theMock.getStuff())
        self.assertEquals(10, theMock.getMoreStuff(1, 2))
        self.assertEquals(None, theMock.getMoreStuff(1, 3))

    def testStubsWhenNoArgsGiven(self):
            theMock = mock()
            when(theMock).getStuff().thenReturn("foo")
            when(theMock).getWidget().thenReturn("bar")

            self.assertEquals("foo", theMock.getStuff())
            self.assertEquals("bar", theMock.getWidget())

    def testStubsConsecutivelyWhenNoArgsGiven(self):
            theMock = mock()
            when(theMock).getStuff().thenReturn("foo").thenReturn("bar")
            when(theMock).getWidget().thenReturn("baz").thenReturn("baz2")

            self.assertEquals("foo", theMock.getStuff())
            self.assertEquals("bar", theMock.getStuff())
            self.assertEquals("bar", theMock.getStuff())
            self.assertEquals("baz", theMock.getWidget())
            self.assertEquals("baz2", theMock.getWidget())
            self.assertEquals("baz2", theMock.getWidget())

    def testStubsWithException(self):
        theMock = mock()
        when(theMock).someMethod().thenRaise(Exception("foo"))

        self.assertRaisesMessage("foo", theMock.someMethod)

    def testStubsAndVerifies(self):
        theMock = mock()
        when(theMock).foo().thenReturn("foo")

        self.assertEquals("foo", theMock.foo())
        verify(theMock).foo()

    def testStubsVerifiesAndStubsAgain(self):
        theMock = mock()

        when(theMock).foo().thenReturn("foo")
        self.assertEquals("foo", theMock.foo())
        verify(theMock).foo()

        when(theMock).foo().thenReturn("next foo")
        self.assertEquals("next foo", theMock.foo())
        verify(theMock, times(2)).foo()

    def testOverridesStubbing(self):
        theMock = mock()

        when(theMock).foo().thenReturn("foo")
        when(theMock).foo().thenReturn("bar")

        self.assertEquals("bar", theMock.foo())

    def testStubsAndInvokesTwiceAndVerifies(self):
        theMock = mock()

        when(theMock).foo().thenReturn("foo")

        self.assertEquals("foo", theMock.foo())
        self.assertEquals("foo", theMock.foo())

        verify(theMock, times(2)).foo()

    def testStubsAndReturnValuesForSameMethodWithDifferentArguments(self):
        theMock = mock()
        when(theMock).getStuff(1).thenReturn("foo")
        when(theMock).getStuff(1, 2).thenReturn("bar")

        self.assertEquals("foo", theMock.getStuff(1))
        self.assertEquals("bar", theMock.getStuff(1, 2))

    def testStubsAndReturnValuesForSameMethodWithDifferentNamedArguments(self):
        repo = mock()
        when(repo).findby(id=6).thenReturn("John May")
        when(repo).findby(name="John").thenReturn(["John May", "John Smith"])

        self.assertEquals("John May", repo.findby(id=6))
        self.assertEquals(["John May", "John Smith"], repo.findby(name="John"))

    def testStubsForMethodWithSameNameAndNamedArgumentsInArbitraryOrder(self):
        theMock = mock()

        when(theMock).foo(first=1, second=2, third=3).thenReturn(True)

        self.assertEquals(True, theMock.foo(third=3, first=1, second=2))

    def testStubsMethodWithSameNameAndMixedArguments(self):
        repo = mock()
        when(repo).findby(1).thenReturn("John May")
        when(repo).findby(1, active_only=True).thenReturn(None)
        when(repo).findby(name="Sarah").thenReturn(["Sarah Connor"])
        when(repo).findby(name="Sarah", active_only=True).thenReturn([])

        self.assertEquals("John May", repo.findby(1))
        self.assertEquals(None, repo.findby(1, active_only=True))
        self.assertEquals(["Sarah Connor"], repo.findby(name="Sarah"))
        self.assertEquals([], repo.findby(name="Sarah", active_only=True))

    def testStubsWithChainedReturnValues(self):
        theMock = mock()
        when(theMock).getStuff().thenReturn("foo") \
                                .thenReturn("bar") \
                                .thenReturn("foobar")

        self.assertEquals("foo", theMock.getStuff())
        self.assertEquals("bar", theMock.getStuff())
        self.assertEquals("foobar", theMock.getStuff())

    def testStubsWithChainedReturnValuesAndException(self):
        theMock = mock()
        when(theMock).getStuff().thenReturn("foo") \
                                .thenReturn("bar") \
                                .thenRaise(Exception("foobar"))

        self.assertEquals("foo", theMock.getStuff())
        self.assertEquals("bar", theMock.getStuff())
        self.assertRaisesMessage("foobar", theMock.getStuff)

    def testStubsWithChainedExceptionAndReturnValue(self):
        theMock = mock()
        when(theMock).getStuff().thenRaise(Exception("foo")) \
                                .thenReturn("bar")

        self.assertRaisesMessage("foo", theMock.getStuff)
        self.assertEquals("bar", theMock.getStuff())

    def testStubsWithChainedExceptions(self):
        theMock = mock()
        when(theMock).getStuff().thenRaise(Exception("foo")) \
                                .thenRaise(Exception("bar"))

        self.assertRaisesMessage("foo", theMock.getStuff)
        self.assertRaisesMessage("bar", theMock.getStuff)

    def testStubsWithReturnValueBeingException(self):
        theMock = mock()
        exception = Exception("foo")
        when(theMock).getStuff().thenReturn(exception)

        self.assertEquals(exception, theMock.getStuff())

    def testLastStubbingWins(self):
        theMock = mock()
        when(theMock).foo().thenReturn(1)
        when(theMock).foo().thenReturn(2)

        self.assertEquals(2, theMock.foo())

    def testStubbingOverrides(self):
        theMock = mock()
        when(theMock).foo().thenReturn(1)
        when(theMock).foo().thenReturn(2).thenReturn(3)

        self.assertEquals(2, theMock.foo())
        self.assertEquals(3, theMock.foo())
        self.assertEquals(3, theMock.foo())

    def testStubsWithMatchers(self):
        theMock = mock()
        when(theMock).foo(any()).thenReturn(1)

        self.assertEquals(1, theMock.foo(1))
        self.assertEquals(1, theMock.foo(100))

    def testStubbingOverrides2(self):
        theMock = mock()
        when(theMock).foo(any()).thenReturn(1)
        when(theMock).foo("oh").thenReturn(2)

        self.assertEquals(2, theMock.foo("oh"))
        self.assertEquals(1, theMock.foo("xxx"))

    def testDoesNotVerifyStubbedCalls(self):
        theMock = mock()
        when(theMock).foo().thenReturn(1)

        verify(theMock, times=0).foo()

    def testStubsWithMultipleReturnValues(self):
        theMock = mock()
        when(theMock).getStuff().thenReturn("foo", "bar", "foobar")

        self.assertEquals("foo", theMock.getStuff())
        self.assertEquals("bar", theMock.getStuff())
        self.assertEquals("foobar", theMock.getStuff())

    def testStubsWithChainedMultipleReturnValues(self):
        theMock = mock()
        when(theMock).getStuff().thenReturn("foo", "bar") \
                                .thenReturn("foobar")

        self.assertEquals("foo", theMock.getStuff())
        self.assertEquals("bar", theMock.getStuff())
        self.assertEquals("foobar", theMock.getStuff())

    def testStubsWithMultipleExceptions(self):
        theMock = mock()
        when(theMock).getStuff().thenRaise(Exception("foo"), Exception("bar"))

        self.assertRaisesMessage("foo", theMock.getStuff)
        self.assertRaisesMessage("bar", theMock.getStuff)

    def testStubsWithMultipleChainedExceptions(self):
        theMock = mock()
        when(theMock).getStuff().thenRaise(Exception("foo"), Exception("bar")) \
                                .thenRaise(Exception("foobar"))

        self.assertRaisesMessage("foo", theMock.getStuff)
        self.assertRaisesMessage("bar", theMock.getStuff)
        self.assertRaisesMessage("foobar", theMock.getStuff)

    def testLeavesOriginalMethodUntouchedWhenCreatingStubFromRealClass(self):
        class Person:
            def get_name(self):
                return "original name"

        # given
        person = Person()
        mockPerson = mock(Person)

        # when
        when(mockPerson).get_name().thenReturn("stubbed name")

        # then
        self.assertEquals("stubbed name", mockPerson.get_name())
        self.assertEquals("original name", person.get_name(),
                          'Original method should not be replaced.')

    def testStubsWithThenAnswer(self):
        m = mock()

        when(m).magic_number().thenAnswer(lambda: 5)

        self.assertEquals(m.magic_number(), 5)

        when(m).add_one(any()).thenAnswer(lambda number: number + 1)

        self.assertEquals(m.add_one(5), 6)
        self.assertEquals(m.add_one(8), 9)

        when(m).do_times(any(), any()).thenAnswer(lambda one, two: one * two)

        self.assertEquals(m.do_times(5, 4), 20)
        self.assertEquals(m.do_times(8, 5), 40)

        when(m).do_dev_magic(any(), any()).thenAnswer(lambda a, b: a/b)

        self.assertEquals(m.do_dev_magic(20, 4), 5)
        self.assertEquals(m.do_dev_magic(40, 5), 8)

        def test_key_words(testing="Magic"):
            return testing + " Stuff"

        when(m).with_key_words().thenAnswer(test_key_words)
        self.assertEquals(m.with_key_words(), "Magic Stuff")

        when(m).with_key_words(testing=any()).thenAnswer(test_key_words)
        self.assertEquals(m.with_key_words(testing="Very Funky"), "Very Funky Stuff")

    def testSubsWithThenAnswerAndMixedArgs(self):
        repo = mock()

        def method_one(value, active_only=False):
            return None

        def method_two(name=None, active_only=False):
            return ["%s Connor" % name]

        def method_three(name=None, active_only=False):
            return [name, active_only, 0]

        when(repo).findby(1).thenAnswer(lambda x: "John May (%d)" % x)
        when(repo).findby(1, active_only=True).thenAnswer(method_one)
        when(repo).findby(name="Sarah").thenAnswer(method_two)
        when(repo).findby(name="Sarah", active_only=True).thenAnswer(method_three)

        self.assertEquals("John May (1)", repo.findby(1))
        self.assertEquals(None, repo.findby(1, active_only=True))
        self.assertEquals(["Sarah Connor"], repo.findby(name="Sarah"))
        self.assertEquals(["Sarah", True, 0], repo.findby(name="Sarah", active_only=True))

if __name__ == '__main__':
    unittest.main()
