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

from unittest import TestLoader as BaseTestLoader, TestSuite
import sys

class TestLoader(BaseTestLoader):
  def loadTestsFromName(self, name, module=None):
    suite = TestSuite()
    for test in findTests(name):
      sys.path.insert(0, name) # python3 compatibility
      suite.addTests(super(TestLoader, self).loadTestsFromName(test))
      del sys.path[0] # python3 compatibility
    return suite

  def loadTestsFromNames(self, names, module=None):
    suite = TestSuite()
    for name in names:
      suite.addTests(self.loadTestsFromName(name))
    return suite

def findTests(dir):
  import os, re
  pattern = re.compile('([a-z]+_)+test\.py$')
  for fileName in os.listdir(dir):
    if pattern.match(fileName):
      yield os.path.join(dir, fileName).replace('.py', '').replace(os.sep, '.')

__all__ = [TestLoader]

