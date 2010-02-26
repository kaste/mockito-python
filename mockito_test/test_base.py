import unittest
import importer

importer.imp()

class TestBase(unittest.TestCase):
  
  def assertRaisesMessage(self, message, function, *params):
    try:
      if (params):
        function(params)
      else:
        function()
        
      self.fail()
    except Exception, e:
      self.assertEquals(message, str(e))
