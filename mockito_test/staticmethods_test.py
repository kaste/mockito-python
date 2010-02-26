from test_base import *
from mockito import *

class Dog:
  @staticmethod
  def bark():
    return "woof"
  
  @staticmethod
  def barkHardly(*args):
    return "woof woof"

class Cat:
  @staticmethod
  def meow():
    return "miau"

class StaticMethodsTest(TestBase):  
  
  def tearDown(self):
    unstub() 

  def testUnstubs(self):     
    when(Dog).bark().thenReturn("miau")
    unstub()
    self.assertEquals("woof", Dog.bark())

#TODO decent test case please :) without testing irrelevant implementation details
  def testUnstubShouldPreserveMethodType(self):
    when(Dog).bark().thenReturn("miau!")
    unstub()
    self.assertTrue(isinstance(Dog.__dict__.get("bark"), staticmethod))  

  def testStubs(self):     
    self.assertEquals("woof", Dog.bark())
    
    when(Dog).bark().thenReturn("miau")
    
    self.assertEquals("miau", Dog.bark())
    
  def testStubsConsecutiveCalls(self):     
    when(Dog).bark().thenReturn(1).thenReturn(2)
    
    self.assertEquals(1, Dog.bark())
    self.assertEquals(2, Dog.bark())
    self.assertEquals(2, Dog.bark())    
    
  def testStubsWithArgs(self):     
    self.assertEquals("woof woof", Dog.barkHardly(1, 2))
    
    when(Dog).barkHardly(1, 2).thenReturn("miau")
    
    self.assertEquals("miau", Dog.barkHardly(1, 2))

  def testStubsButDoesNotMachArguments(self): 
    self.assertEquals("woof woof", Dog.barkHardly(1, "anything"))
    
    when(Dog, strict=False).barkHardly(1, 2).thenReturn("miau")
    
    self.assertEquals(None, Dog.barkHardly(1))
    
  def testStubsMultipleClasses(self): 
    when(Dog).barkHardly(1, 2).thenReturn(1)
    when(Dog).bark().thenReturn(2)
    when(Cat).meow().thenReturn(3)
    
    self.assertEquals(1, Dog.barkHardly(1, 2))
    self.assertEquals(2, Dog.bark())
    self.assertEquals(3, Cat.meow())

    unstub()

    self.assertEquals("woof", Dog.bark())
    self.assertEquals("miau", Cat.meow())

  def testVerifiesSuccesfully(self):     
    when(Dog).bark().thenReturn("boo")
    
    Dog.bark()
    
    verify(Dog).bark()
    
  def testVerifiesWithArguments(self):     
    when(Dog).barkHardly(1, 2).thenReturn("boo")
    
    Dog.barkHardly(1, 2)
    
    verify(Dog).barkHardly(1, any())

  def testFailsVerification(self):
    when(Dog).bark().thenReturn("boo")

    Dog.bark()
    
    self.assertRaises(VerificationError, verify(Dog).barkHardly, (1,2))
    
  def testFailsOnInvalidArguments(self):
    when(Dog).bark().thenReturn("boo")

    Dog.barkHardly(1, 2)
    
    self.assertRaises(VerificationError, verify(Dog).barkHardly, (1,20))    
    
  def testFailsOnNumberOfCalls(self):
    when(Dog).bark().thenReturn("boo")

    Dog.bark()
    
    self.assertRaises(VerificationError, verify(Dog, times(2)).bark)
    
  def testStubsAndVerifies(self):
    when(Dog).bark().thenReturn("boo")
    
    self.assertEquals("boo", Dog.bark())
    
    verify(Dog).bark()

  def testStubsTwiceAndUnstubs(self):
    when(Dog).bark().thenReturn(1)
    when(Dog).bark().thenReturn(2)
    
    self.assertEquals(2, Dog.bark())
    
    unstub()
    
    self.assertEquals("woof", Dog.bark())
    
  def testDoesNotVerifyStubbedCalls(self):
    when(Dog).bark().thenReturn(1)

    verify(Dog, times=0).bark()    

if __name__ == '__main__':
  unittest.main()
