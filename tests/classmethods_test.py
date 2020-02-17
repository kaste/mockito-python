# Copyright (c) 2008-2016 Szczepan Faber, Serhiy Oplakanets, Herr Kaste
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from mockito import unstub, verify, when
from mockito.verification import VerificationError

from .test_base import TestBase


class Dog:
    @classmethod
    def bark(cls):
        return "woof!"


class Cat:
    @classmethod
    def meow(cls, m):
        return cls.__name__ + " " + str(m)


class Lion(object):
    @classmethod
    def roar(cls):
        return "Rrrrr!"


class ClassMethodsTest(TestBase):

    def tearDown(self):
        unstub()

    def testUnstubs(self):
        when(Dog).bark().thenReturn("miau!")
        unstub()
        self.assertEqual("woof!", Dog.bark())

    # TODO decent test case please :) without testing irrelevant implementation
    # details
    def testUnstubShouldPreserveMethodType(self):
        when(Dog).bark().thenReturn("miau!")
        unstub()
        self.assertTrue(isinstance(Dog.__dict__.get("bark"), classmethod))

    def testStubs(self):
        self.assertEqual("woof!", Dog.bark())

        when(Dog).bark().thenReturn("miau!")

        self.assertEqual("miau!", Dog.bark())

    def testStubsClassesDerivedFromTheObjectClass(self):
        self.assertEqual("Rrrrr!", Lion.roar())

        when(Lion).roar().thenReturn("miau!")

        self.assertEqual("miau!", Lion.roar())

    def testVerifiesMultipleCallsOnClassmethod(self):
        when(Dog).bark().thenReturn("miau!")

        Dog.bark()
        Dog.bark()

        verify(Dog, times=2).bark()

    def testFailsVerificationOfMultipleCallsOnClassmethod(self):
        when(Dog).bark().thenReturn("miau!")

        Dog.bark()

        self.assertRaises(VerificationError, verify(Dog, times=2).bark)

    def testStubsAndVerifiesClassmethod(self):
        when(Dog).bark().thenReturn("miau!")

        self.assertEqual("miau!", Dog.bark())

        verify(Dog).bark()

    def testPreservesClassArgumentAfterUnstub(self):
        self.assertEqual("Cat foo", Cat.meow("foo"))

        when(Cat).meow("foo").thenReturn("bar")

        self.assertEqual("bar", Cat.meow("foo"))

        unstub()

        self.assertEqual("Cat foo", Cat.meow("foo"))


class Retriever:
    @classmethod
    def retrieve(cls, item):
        return item


class TrickDog(Dog, Retriever):
    pass


class InheritedClassMethodsTest(TestBase):

    def tearDown(self):
        unstub()

    def testUnstubs(self):
        when(TrickDog).bark().thenReturn("miau!")
        when(TrickDog).retrieve("stick").thenReturn("ball")
        unstub()
        self.assertEqual("woof!", TrickDog.bark())
        self.assertEqual("stick", TrickDog.retrieve("stick"))

    def testStubs(self):
        self.assertEqual("woof!", TrickDog.bark())
        self.assertEqual("stick", TrickDog.retrieve("stick"))

        when(TrickDog).bark().thenReturn("miau!")
        when(TrickDog).retrieve("stick").thenReturn("ball")

        self.assertEqual("miau!", TrickDog.bark())
        self.assertEqual("ball", TrickDog.retrieve("stick"))

    def testVerifiesMultipleCallsOnClassmethod(self):
        when(TrickDog).bark().thenReturn("miau!")
        when(TrickDog).retrieve("stick").thenReturn("ball")

        TrickDog.bark()
        TrickDog.bark()

        TrickDog.retrieve("stick")
        TrickDog.retrieve("stick")

        verify(TrickDog, times=2).bark()
        verify(TrickDog, times=2).retrieve("stick")

    def testFailsVerificationOfMultipleCallsOnClassmethod(self):
        when(TrickDog).bark().thenReturn("miau!")
        when(TrickDog).retrieve("stick").thenReturn("bark")

        TrickDog.bark()
        TrickDog.retrieve("stick")

        self.assertRaises(VerificationError, verify(TrickDog, times=2).bark)
        self.assertRaises(VerificationError, verify(TrickDog,
                                                    times=2).retrieve)

    def testStubsAndVerifiesClassmethod(self):
        when(TrickDog).bark().thenReturn("miau!")
        when(TrickDog).retrieve("stick").thenReturn("ball")

        self.assertEqual("miau!", TrickDog.bark())
        self.assertEqual("ball", TrickDog.retrieve("stick"))

        verify(TrickDog).bark()
        verify(TrickDog).retrieve("stick")

    def testPreservesSuperClassClassMethodWhenStubbed(self):
        self.assertEqual("woof!", Dog.bark())
        self.assertEqual("stick", Retriever.retrieve("stick"))

        self.assertEqual("woof!", TrickDog.bark())
        self.assertEqual("stick", TrickDog.retrieve("stick"))

        when(TrickDog).bark().thenReturn("miau!")
        when(TrickDog).retrieve("stick").thenReturn("ball")

        self.assertEqual("miau!", TrickDog.bark())
        self.assertEqual("ball", TrickDog.retrieve("stick"))

        self.assertEqual("woof!", Dog.bark())
        self.assertEqual("stick", Retriever.retrieve("stick"))

    def testUnStubWorksOnClassAndSuperClass(self):
        when(Retriever).retrieve("stick").thenReturn("ball")
        when(TrickDog).retrieve("stick").thenReturn("cat")
        unstub()
        self.assertEqual("stick", TrickDog.retrieve("stick"))

    def testDoubleStubStubWorksAfterUnstub(self):
        when(TrickDog).retrieve("stick").thenReturn("ball")
        when(TrickDog).retrieve("stick").thenReturn("cat")
        unstub()
        self.assertEqual("stick", TrickDog.retrieve("stick"))
