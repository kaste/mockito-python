import unittest
from mockito_classmethods_test import * 
from mockito_matchers_test import * 
from mockito_staticmethods_test import * 
from mockito_stubbing_test import * 
from mockito_verification_test import * 
from mockito_modulefunctions_test import *
from mockito_demo_test import *  
from mockito_verification_errors_test import *  

#TODO: can this be smarter - i can forget to put a test class here:
tests = [MockitoClassMethodsTest, MockitoMatchersTest, MockitoStaticMethodsTest, 
         MockitoStubbingTest, MockitoVerificationTest, MockitoModuleFunctionsTest,
         MockitoDemoTest, MockitoVerificationErrorsTest]

all = unittest.TestSuite()
for test in tests: all.addTest(unittest.makeSuite(test))
unittest.TextTestRunner(verbosity=2).run(all)