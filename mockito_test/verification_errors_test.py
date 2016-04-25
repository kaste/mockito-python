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
from mockito import (mock, when, verify, VerificationError,
                     verifyNoMoreInteractions)
from mockito.verification import never


class VerificationErrorsTest(TestBase):

    def testPrintsNicely(self):
        theMock = mock()
        try:
            verify(theMock).foo()
        except VerificationError as e:
            self.assertEquals("\nWanted but not invoked: foo()", str(e))

    def testPrintsNicelyOneArgument(self):
        theMock = mock()
        try:
            verify(theMock).foo("bar")
        except VerificationError as e:
            self.assertEquals("\nWanted but not invoked: foo('bar')", str(e))

    def testPrintsNicelyArguments(self):
        theMock = mock()
        try:
            verify(theMock).foo(1, 2)
        except VerificationError as e:
            self.assertEquals("\nWanted but not invoked: foo(1, 2)", str(e))

    def testPrintsNicelyStringArguments(self):
        theMock = mock()
        try:
            verify(theMock).foo(1, 'foo')
        except VerificationError as e:
            self.assertEquals("\nWanted but not invoked: foo(1, 'foo')", str(e))

    def testPrintKeywordArgumentsNicely(self):
        theMock = mock()
        try:
            verify(theMock).foo(foo='foo', one=1)
        except VerificationError as e:
            message = str(e)
            # We do not want to guarantee any order of arguments here
            self.assertTrue("foo='foo'" in message)
            self.assertTrue("one=1" in message)

    def testPrintsOutThatTheActualAndExpectedInvocationCountDiffers(self):
        theMock = mock()
        when(theMock).foo().thenReturn(0)

        theMock.foo()
        theMock.foo()

        try:
            verify(theMock).foo()
        except VerificationError as e:
            self.assertEquals("\nWanted times: 1, actual times: 2", str(e))


    # TODO: implement
    def disabled_PrintsNicelyWhenArgumentsDifferent(self):
        theMock = mock()
        theMock.foo('foo', 1)
        try:
            verify(theMock).foo(1, 'foo')
        except VerificationError as e:
            self.assertEquals("""Arguments are different.
                              Wanted: foo(1, 'foo')
                              Actual: foo('foo', 1)""", str(e))

    def testPrintsUnwantedInteraction(self):
        theMock = mock()
        theMock.foo(1, 'foo')
        try:
            verifyNoMoreInteractions(theMock)
        except VerificationError as e:
            self.assertEquals("\nUnwanted interaction: foo(1, 'foo')", str(e))

    def testPrintsNeverWantedInteractionsNicely(self):
            theMock = mock()
            theMock.foo()
            self.assertRaisesMessage("\nUnwanted invocation of foo(), times: 1",
                                     verify(theMock, never).foo)

if __name__ == '__main__':
    unittest.main()
