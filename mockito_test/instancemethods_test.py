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
from mockito import *
from mockito.invocation import InvocationError

class Dog(object):
    def waggle(self):
        return "Wuff!"

    def bark(self, sound):
        return "%s!" % sound

    def do_default_bark(self):
        return self.bark('Wau')

class InstanceMethodsTest(TestBase):
    def tearDown(self):
        unstub()

    def testUnstubAnInstanceMethod(self):
        original_method = Dog.waggle
        when(Dog).waggle().thenReturn('Nope!')

        unstub()

        rex = Dog()
        self.assertEquals('Wuff!', rex.waggle())
        self.assertEquals(original_method, Dog.waggle)

    def testStubAnInstanceMethod(self):
        when(Dog).waggle().thenReturn('Boing!')

        rex = Dog()
        self.assertEquals('Boing!', rex.waggle())

    def testStubsAnInstanceMethodWithAnArgument(self):
        when(Dog).bark('Miau').thenReturn('Wuff')

        rex = Dog()
        self.assertEquals('Wuff', rex.bark('Miau'))
        #self.assertEquals('Wuff', rex.bark('Wuff'))

    def testInvocateAStubbedMethodFromAnotherMethod(self):
        when(Dog).bark('Wau').thenReturn('Wuff')

        rex = Dog()
        self.assertEquals('Wuff', rex.do_default_bark())
        verify(Dog).bark('Wau')

    def testYouCantStubAnUnknownMethodInStrictMode(self):
        try:
            when(Dog).barks('Wau').thenReturn('Wuff')
            self.fail('Stubbing an unknown method should have thrown a exception')
        except InvocationError:
            pass

    def testThrowEarlyIfCallingAStubbedMethodWithUnexpectedArgumentsInStrictMode(self):
        when(Dog).bark('Miau').thenReturn('Wuff')
        rex = Dog()
        try:
            rex.bark('Shhh')
            self.fail('Calling a stubbed method with unexpected arguments '
                      'should have thrown.')
        except InvocationError:
            pass

    def testCallingAStubbedMethodWithUnexpectedArgumentsReturnsNoneIfNotStrict(self):
        when(Dog, strict=False).bark('Miau').thenReturn('Wuff')
        rex = Dog()
        self.assertEquals(None, rex.bark('Shhh'))

    def testStubInstancesInsteadOfClasses(self):
        rex = Dog()
        when(rex).bark('Miau').thenReturn('Wuff')

        self.assertEquals('Wuff', rex.bark('Miau'))
        verify(rex, times=1).bark(any())

        max = Dog()
        self.assertEquals('Miau!', max.bark('Miau'))

    def testNoExplicitReturnValueMeansNone(self):
        when(Dog).bark('Miau').thenReturn()
        rex = Dog()

        self.assertEquals(None, rex.bark('Miau'))

    def testForgottenThenReturnMeansReturnNone(self):
        when(Dog).bark('Miau')
        when(Dog).waggle()
        rex = Dog()

        self.assertEquals(None, rex.bark('Miau'))
        self.assertEquals(None, rex.waggle())

if __name__ == '__main__':
    unittest.main()
