from test_base import *
from mockito import mock, verify, contains

class MatchersTest(TestBase):
  def testVerifiesUsingContainsMatcher(self):
    ourMock = mock()
    ourMock.foo("foobar")
    
    verify(ourMock).foo(contains("foo"))
    verify(ourMock).foo(contains("bar"))

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
