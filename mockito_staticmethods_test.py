from test_base import *
from mockito import *

class Dog():
  @staticmethod
  def bark():
    return "woof!"
  
  @staticmethod
  def barkHardly(*args):
    return "woof woof!"

class Cat():
  @staticmethod
  def meow():
    return "miau!"

class MockitoStaticmethodsTest(TestBase):   

  def testStubs(self):     
    self.assertEquals("woof!", Dog.bark())
    
    when(Dog).bark().thenReturn("miau!")
    
    self.assertEquals("miau!", Dog.bark())
    
  def testStubsWithArgs(self):     
    self.assertEquals("woof woof!", Dog.barkHardly(1, 2))
    
    when(Dog).barkHardly(1, 2).thenReturn("miau!")
    
    self.assertEquals("miau!", Dog.barkHardly(1, 2))

  def xtestStubsButDoesNotMachArguments(self): 
    self.assertEquals("woof woof!", Dog.barkHardly(1, "anything"))
    
    when(Dog).barkHardly(1, 2).thenReturn("miau!")
    
    self.assertEquals(None, Dog.barkHardly(1))

  def xtestUnstubs(self):     
    when(Dog).bark().thenReturn("miau!")
    unstub(Dog)
    self.assertEquals("woof!", Dog.bark())
    
  def xtestVerifiesSuccesfully(self):     
    when(Dog).bark().thenReturn("miau!")
    
    Dog.bark()
    
    verify(Dog).bark()
    
  def xtestFailsVerification(self):
    when(Dog).bark().thenReturn("miau!")

    Dog.bark()
    
    self.assertRaises(VerificationError, verify(Dog, times(2)).bark)

  def xtestStubsAndVerifiesClassmethod(self):
    dog = ClassMock(Dog)
    when(dog).bark().thenReturn("miau!")
    
    self.assertEquals("miau!", Dog.bark())
    
    verify(dog).bark()

  # TODO: fix the code for failing test
  #def testStubsTwoMethodsFromTwoDifferentClasses(self):
  #  dog = ClassMock(Dog)
  #  when(dog).bark().thenReturn("miau!")
  #  cat = ClassMock(Cat)
  #  when(cat).meow().thenReturn("woof!")
  #  
  #  self.assertEquals("miau!", Dog.bark())
  #  self.assertEquals("woof!", Cat.meow())

if __name__ == '__main__':
  unittest.main()