#!/usr/bin/env python
# coding: utf-8

import unittest

class TestBase(unittest.TestCase):
  
  def __init__(self, *args, **kwargs):
    unittest.TestCase.__init__(self, *args, **kwargs)
    
  def assertRaisesMessage(self, message, function, *params):
    try:
      if (params):
        function(params)
      else:
        function()        
      self.fail('Exception with message "%s" expected, but never raised' % (message))
    except Exception, e:
      # TODO: self.fail() raises AssertionError which is caught here and error message becomes hardly understadable 
      self.assertEquals(message, str(e))    

main = unittest.main
