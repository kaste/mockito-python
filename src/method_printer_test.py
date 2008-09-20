from test_base import *
from method_printer import *

class MethodPrinterTest(TestBase):
  
  def testPrintsMethod(self):
    self.assertEquals("foo()", MethodPrinter().str("foo"))
    
if __name__ == '__main__':
  unittest.main()