import unittest
from mockito_classmethods_test import * 
from mockito_matchers_test import * 
from mockito_staticmethods_test import * 
from mockito_stubbing_test import * 
from mockito_verification_test import * 

#TODO dodgy, use loading all test from module
t1 = unittest.TestLoader().loadTestsFromTestCase(MockitoClassMethodsTest)
t2 = unittest.TestLoader().loadTestsFromTestCase(MockitoMatchersTest)
t3 = unittest.TestLoader().loadTestsFromTestCase(MockitoStaticMethodsTest)
t4 = unittest.TestLoader().loadTestsFromTestCase(MockitoStubbingTest)
t5 = unittest.TestLoader().loadTestsFromTestCase(MockitoVerificationTest)

all = unittest.TestSuite([t1, t2, t3, t4, t5])

unittest.TextTestRunner(verbosity=2).run(all)