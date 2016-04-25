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


from mockito_test.test_base import TestBase
from mockito import spy, verify, VerificationError


class Dummy:
    def foo(self):
        return "foo"

    def bar(self):
        raise TypeError

    def return_args(self, *args, **kwargs):
        return (args, kwargs)


class SpyingTest(TestBase):
    def testPreservesReturnValues(self):
        dummy = Dummy()
        spiedDummy = spy(dummy)
        self.assertEquals(dummy.foo(), spiedDummy.foo())

    def testPreservesSideEffects(self):
        dummy = spy(Dummy())
        self.assertRaises(TypeError, dummy.bar)

    def testPassesArgumentsCorrectly(self):
        dummy = spy(Dummy())
        self.assertEquals((('foo', 1), {'bar': 'baz'}),
                          dummy.return_args('foo', 1, bar='baz'))

    def testIsVerifiable(self):
        dummy = spy(Dummy())
        dummy.foo()
        verify(dummy).foo()
        self.assertRaises(VerificationError, verify(dummy).bar)

    def testRaisesAttributeErrorIfNoSuchMethod(self):
        dummy = spy(Dummy())
        try:
            dummy.lol()
            self.fail("Should fail if no such method.")
        except AttributeError as e:
            self.assertEquals("You tried to call method 'lol' which 'Dummy' "
                              "instance does not have.", str(e))
