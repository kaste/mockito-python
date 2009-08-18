from test_base import *
from mockito import *
import inspect

class Dog(object):
    def waggle(self):
        return "Wuff!"
    def bark(self, sound):
        return "%s!" % sound
    
    def do_default_bark(self):
        return self.bark('Wau')
    
class MockitoMockedObjectsTest(TestBase):
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
        

if __name__ == '__main__':
    unittest.main()