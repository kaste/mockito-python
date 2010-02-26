from test_base import *
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
        
    def testCallingAStubbedMethodWithUnexpectedArgumentsShouldThrow(self):
        when(Dog).bark('Miau').thenReturn('Wuff')
        
        rex = Dog()
        try:
            rex.bark('Shhhh')
            self.fail('Calling a stubbed method with unexpected arguments should have thrown')
        except InvocationError:
            pass
        
    def testStubInstancesInsteadOfClasses(self):
        rex = Dog()
        when(rex).bark('Miau').thenReturn('Wuff')
        
        self.assertEquals('Wuff', rex.bark('Miau'))
        verify(rex, times=1).bark(any())

        max = Dog()
        self.assertEquals('Miau!', max.bark('Miau'))
        
        
if __name__ == '__main__':
    unittest.main()
