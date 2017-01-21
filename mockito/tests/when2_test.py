
import sys
import types

from mockito import when2 as when, patch

PY3 = sys.version_info >= (3,)


def newmethod(fn, obj):
    if PY3:
        return types.MethodType(fn, obj)
    else:
        return types.MethodType(fn, obj, obj.__class__)

class Dog(object):
    def bark(self, sound):
        return sound

    def bark_hard(self, sound):
        return sound + '!'


class TestMockito2:
    def testWhen2(self):
        rex = Dog()
        when(rex.bark, 'Miau').thenReturn('Wuff')


    def testPatch(self):
        rex = Dog()
        patch(rex.bark, lambda sound: sound + '!')
        assert rex.bark('Miau') == 'Miau!'


    def testPatch2(self):
        rex = Dog()
        patch(rex.bark, rex.bark_hard)
        assert rex.bark('Miau') == 'Miau!'

    def testPatch3(self):
        rex = Dog()

        def f(self, sound):
            return self.bark_hard(sound)

        f = newmethod(f, rex)
        patch(rex.bark, f)

        assert rex.bark('Miau') == 'Miau!'
