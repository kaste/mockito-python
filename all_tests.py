import unittest
from mockito_classmethods_test import * 
from mockito_matchers_test import * 
from mockito_staticmethods_test import * 
from mockito_stubbing_test import * 
from mockito_verification_test import * 
from mockito_modulemethods_test import * 

tests = [MockitoClassMethodsTest, MockitoMatchersTest, MockitoStaticMethodsTest, 
         MockitoStubbingTest, MockitoVerificationTest, MockitoModuleMethodsTest]

all = unittest.TestSuite()
for test in tests: all.addTest(unittest.makeSuite(test))
unittest.TextTestRunner(verbosity=2).run(all)