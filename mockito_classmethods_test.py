from test_base import *
from mockito import *

class Dog():
  @classmethod
  def bark(cls):
    return "woof!"

class MockitoClassMethodsTest(TestBase):   

  def testVerifiesMultipleCallsOnClassmethod(self):     
    dog = ClassMock(Dog)
    when(dog).bark().thenReturn("miau!")

    for i in range(0, 10): Dog.bark()
    
    verify(dog, times(10)).bark()
    
  def testFailsVerificationOfMultipleCallsOnClassmethod(self):
    dog = ClassMock(Dog)
    when(dog).bark().thenReturn("miau!")

    Dog.bark()
    
    self.assertRaises(VerificationError, verify(dog, times(2)).bark)

  def testStubsAndVerifiesClassmethod(self):
    dog = ClassMock(Dog)
    when(dog).bark().thenReturn("miau!")
    
    self.assertEquals("miau!", Dog.bark())
    
    verify(dog).bark()
    
if __name__ == '__main__':
  unittest.main()    