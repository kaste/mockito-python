from test_base import *
from mockito import *

# TODO: add more test cases (create a base test class for both static and class methods?)

class Dog():
  @classmethod
  def bark(cls):
    return "woof!"

class MockitoClassMethodsTest(TestBase):   

  def tearDown(self):
    unstub() 

  def testUnstubs(self):     
    when(Dog).bark().thenReturn("miau!")
    unstub()
    self.assertEquals("woof!", Dog.bark())
  
  def testStubs(self):     
    self.assertEquals("woof!", Dog.bark())
    
    when(Dog).bark().thenReturn("miau!")
    
    self.assertEquals("miau!", Dog.bark())
    
  def testVerifiesMultipleCallsOnClassmethod(self):     
    when(Dog).bark().thenReturn("miau!")

    for i in range(0, 10): Dog.bark()
    
    verify(Dog, times(10)).bark()
    
  def testFailsVerificationOfMultipleCallsOnClassmethod(self):
    when(Dog).bark().thenReturn("miau!")

    Dog.bark()
    
    self.assertRaises(VerificationError, verify(Dog, times(2)).bark)

  def testStubsAndVerifiesClassmethod(self):
    when(Dog).bark().thenReturn("miau!")
    
    self.assertEquals("miau!", Dog.bark())
    
    verify(Dog).bark()
    
if __name__ == '__main__':
  unittest.main()    