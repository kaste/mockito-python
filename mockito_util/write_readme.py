#   Copyright (c) 2008-2013 Szczepan Faber, Serhiy Oplakanets, Herr Kaste
#
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#   of this software and associated documentation files (the "Software"), to deal
#   in the Software without restriction, including without limitation the rights
#   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#   copies of the Software, and to permit persons to whom the Software is
#   furnished to do so, subject to the following conditions:
#
#   The above copyright notice and this permission notice shall be included in
#   all copies or substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#   THE SOFTWARE.

import os
import re

def openFile(f, m='r'):
  if (os.path.exists(f)):
    return open(f, m)
  else:
    return open('../' + f, m)
    
demo_test = '  '.join(openFile('mockito_test/demo_test.py').readlines())
demo_test = demo_test.split('#DELIMINATOR')[1]

readme_before = ''.join(openFile('README.rst').readlines())
token = 'Basic usage:'
readme_after = re.compile(token + '.*', re.S).sub(token + '\n' + demo_test, readme_before)

if (readme_before != readme_after):  
  readme_file = openFile('README.rst', 'w')
  readme_file.write(readme_after)
  print "README updated"
else:
  print "README update not required" 
