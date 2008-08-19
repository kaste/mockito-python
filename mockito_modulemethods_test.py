from test_base import *
from mockito import * 
import os

class MockitoModuleMethodsTest(TestBase):
  def tearDown(self):
    unstub() 

  def testUnstubs(self):     
    when(os.path).exists("test").thenReturn(True)
    unstub()
    self.assertEquals(False, os.path.exists("test"))
      
  def testStubs(self):
    when(os.path).exists("test").thenReturn(True)
    
    self.assertEquals(True, os.path.exists("test"))

  def testStubsConsecutiveCalls(self):     
    when(os.path).exists("test").thenReturn(False).thenReturn(True)
    
    self.assertEquals(False, os.path.exists("test"))
    self.assertEquals(True, os.path.exists("test"))

  def testStubsMultipleClasses(self):
    when(os.path).exists("test").thenReturn(True)
    when(os.path).dirname("/usr/local/this").thenReturn("mocked")

    self.assertEquals(True, os.path.exists("test"))
    self.assertEquals("mocked", os.path.dirname(any(str)))     

  def testVerifiesSuccesfully(self):     
    when(os.path).exists("test").thenReturn(True)
    
    os.path.exists("test")
    
    verify(os.path).exists("test")
    
  def testFailsVerification(self):
    when(os.path).exists("test").thenReturn(True)

    self.assertRaises(VerificationError, verify(os.path).exists, "test")

  def testFailsOnNumberOfCalls(self):
    when(os.path).exists("test").thenReturn(True)

    os.path.exists("test")
    
    self.assertRaises(VerificationError, verify(os.path, times(2)).exists, "test")

  def testStubsTwiceAndUnstubs(self):
    when(os.path).exists("test").thenReturn(False)
    when(os.path).exists("test").thenReturn(True)
    
    self.assertEquals(True, os.path.exists("test"))
    
    unstub()
    
    self.assertEquals(False, os.path.exists("test"))

if __name__ == '__main__':
  unittest.main()