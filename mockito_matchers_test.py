from test_base import *
from mockito import *

class MockitoMatchersTest(TestBase):
  def testVerifiesUsingContainsMatcher(self):
    mock = Mock()
    mock.foo("foobar")
    
    verify(mock).foo(contains("foo"))
    verify(mock).foo(contains("bar"))

class ContainsMatcherTest(TestBase):
  def testShouldSatisfiySubstringOfGivenString(self):
    self.assertTrue(contains("foo").satisfies("foobar"))      

  def testShouldSatisfySameString(self):
    self.assertTrue(contains("foobar").satisfies("foobar"))      

  def testShouldNotSatisfiyStringWhichIsNotSubstringOfGivenString(self):
    self.assertFalse(contains("barfoo").satisfies("foobar"))      

  def testShouldNotSatisfiyEmptyString(self):
    self.assertFalse(contains("").satisfies("foobar"))      

  def testShouldNotSatisfiyNone(self):
    self.assertFalse(contains(None).satisfies("foobar"))      

if __name__ == '__main__':
  unittest.main()