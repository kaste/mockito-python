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

import mockito_util.write_readme

#all below code will be merged with README
#DELIMINATOR
import unittest
from mockito import mock, when, verify

class DemoTest(unittest.TestCase):
  def testStubbing(self):
    # create a mock
    ourMock = mock()

    # stub it
    when(ourMock).getStuff("cool").thenReturn("cool stuff")
    
    # use the mock
    self.assertEqual("cool stuff", ourMock.getStuff("cool"))
    
    # what happens when you pass different argument?
    self.assertEqual(None, ourMock.getStuff("different argument"))
    
  def testVerification(self):
    # create a mock
    theMock = mock()

    # use the mock
    theMock.doStuff("cool")
    
    # verify the interactions. Method and parameters must match. Otherwise verification error.
    verify(theMock).doStuff("cool")
  
#DELIMINATOR
#all above code will be merged with README
if __name__ == '__main__':    
    unittest.main()    

