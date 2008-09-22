from test_base import *
from method_printer import *

class MethodPrinterTest(TestBase):
  
  def testPrintsMethod(self):
    self.assertEquals("foo()", MethodPrinter().printIt("foo"))
    
  def testPrintsMethodAndArgs(self):
    self.assertEquals("foo(1, 2)", MethodPrinter().printIt("foo", 1, 2))    
    
if __name__ == '__main__':
  unittest.main()