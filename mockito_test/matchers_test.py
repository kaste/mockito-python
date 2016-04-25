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
from mockito import mock, verify, contains


class MatchersTest(TestBase):
    def testVerifiesUsingContainsMatcher(self):
        ourMock = mock()
        ourMock.foo("foobar")

        verify(ourMock).foo(contains("foo"))
        verify(ourMock).foo(contains("bar"))


class ContainsMatcherTest(TestBase):
    def testShouldSatisfiySubstringOfGivenString(self):
        self.assertTrue(contains("foo").matches("foobar"))

    def testShouldSatisfySameString(self):
        self.assertTrue(contains("foobar").matches("foobar"))

    def testShouldNotSatisfiyStringWhichIsNotSubstringOfGivenString(self):
        self.assertFalse(contains("barfoo").matches("foobar"))

    def testShouldNotSatisfiyEmptyString(self):
        self.assertFalse(contains("").matches("foobar"))

    def testShouldNotSatisfiyNone(self):
        self.assertFalse(contains(None).matches("foobar"))

if __name__ == '__main__':
    unittest.main()
