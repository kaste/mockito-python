
from mockito import when2 as when, patch
from mockito.utils import newmethod



class Dog(object):
    def bark(self, sound):
        return sound

    def bark_hard(self, sound):
        return sound + '!'


class TestMockito2:
    def testWhen2(self):
        rex = Dog()
        when(rex.bark, 'Miau').thenReturn('Wuff')
        when(rex.bark, 'Miau').thenReturn('Grrr')
        assert rex.bark('Miau') == 'Grrr'


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
