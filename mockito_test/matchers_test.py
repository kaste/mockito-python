from test_base import *
from mockito import *

class MatchersTest(TestBase):
  def testVerifiesUsingContainsMatcher(self):
    mock = Mock()
    mock.foo("foobar")
    
    verify(mock).foo(contains("foo"))
    verify(mock).foo(contains("bar"))

class ContainsMatcherTest(TestBase):
  def testShouldSatisfiySubstringOfGivenString(self):
    self.assertTrue(contains("foo").matches("foobar"))      

  def testShouldSatisfySameString(self):
    self.assertTrue(contains("foobar").matches("foobar"))      

  def testShouldNotSatisfiyStringWhichIsNotSubstringOfGivenString(self):
    self.assertFalse(contains("barfoo").matches("foobar"))      

  def testShouldNotSatisfiyEmptyString(self):
    self.assertFalse(contains("").matches("foobar"))      

  def testShouldNotSatisfiyNone(self):
    self.assertFalse(contains(None).matches("foobar"))      

if __name__ == '__main__':
  unittest.main()
