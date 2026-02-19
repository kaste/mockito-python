
import sys

import pytest
from mockito import mock, when
from mockito.invocation import AnswerError

from . import module
from .test_base import TestBase


class Dog:
    def __init__(self, huge=False):
        self.huge = huge

    def bark(self):
        if self.huge:
            return "woof"
        else:
            return "waf ! waf ! waf ! waf ! waf ! waf !"

    @classmethod
    def class_bark(cls):
        return cls.__name__ + " woof"

    @staticmethod
    def static_bark(arg):
        return str(arg) + " woof"


class FalsyCallable:
    def __bool__(self):
        return False

    def __call__(self, *args, **kwargs):
        return "falsy callable works"


class HasFalsyCallable:
    call = FalsyCallable()


class CallOriginalImplementationTest(TestBase):

    def testClassMethod(self):
        when(Dog).class_bark().thenCallOriginalImplementation()

        self.assertEqual("Dog woof", Dog.class_bark())

    def testStaticMethod(self):
        when(Dog).static_bark("wif").thenCallOriginalImplementation()
        self.assertEqual("wif woof", Dog.static_bark("wif"))

    def testStaticMethodOnInstance(self):
        dog = Dog()
        when(Dog).static_bark("wif").thenCallOriginalImplementation()
        self.assertEqual("wif woof", dog.static_bark("wif"))

    def testMethod(self):
        when(Dog).bark().thenCallOriginalImplementation()

        assert Dog(huge=True).bark() == "woof"

    def testMethodOnInstance(self):
        dog = Dog(huge=True)
        when(dog).bark().thenCallOriginalImplementation()

        assert dog.bark() == "woof"

    def testFunction(self):
        when(module).one_arg(Ellipsis).thenCallOriginalImplementation()
        assert module.one_arg("woof") == "woof"

    def testChain(self):
        when(module).one_arg(Ellipsis) \
                    .thenReturn("wif") \
                    .thenCallOriginalImplementation() \
                    .thenReturn("waf")
        assert module.one_arg("woof") == "wif"
        assert module.one_arg("woof") == "woof"
        assert module.one_arg("woof") == "waf"

    def testDumbMockHasNoOriginalImplementations(self):
        dog = mock()
        answer_selector = when(dog).bark()
        with pytest.raises(AnswerError) as exc:
            answer_selector.thenCallOriginalImplementation()

        if sys.version_info >= (3, 0):
            class_str_value = "mockito.mocking.mock.<locals>.Dummy"
        else:
            class_str_value = "mockito.mocking.Dummy"
        assert str(exc.value) == (
            "'<class '%s'>' "
            "has no original implementation for 'bark'."
        ) % class_str_value

    def testSpeccedMockHasOriginalImplementations(self):
        dog = mock({"huge": True}, spec=Dog)
        when(dog).bark().thenCallOriginalImplementation()
        assert dog.bark() == "woof"

    def testFalsyCallableOriginalImplementation(self):
        when(HasFalsyCallable).call().thenCallOriginalImplementation()
        assert HasFalsyCallable.call() == "falsy callable works"
