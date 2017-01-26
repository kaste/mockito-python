
import pytest

from mockito import when2, patch, spy2, verify
from mockito.utils import newmethod


import os


class Dog(object):
    def bark(self, sound):
        return sound

    def bark_hard(self, sound):
        return sound + '!'


@pytest.mark.usefixtures('unstub')
class TestMockito2:
    def testWhen2(self):
        rex = Dog()
        when2(rex.bark, 'Miau').thenReturn('Wuff')
        when2(rex.bark, 'Miau').thenReturn('Grrr')
        assert rex.bark('Miau') == 'Grrr'

    def testSafeWhen2(self):
        # This test is a bit flaky bc pytest does not like a patched
        # `os.path.exists` module.
        when2(os.path.commonprefix, '/Foo').thenReturn(False)
        when2(os.path.commonprefix, '/Foo').thenReturn(True)
        when2(os.path.exists, '/Foo').thenReturn(True)

        assert os.path.commonprefix('/Foo')
        assert os.path.exists('/Foo')

    def testSafePatch(self):
        patch(os.path.commonprefix, lambda m: 'yup')
        patch(os.path.commonprefix, lambda m: 'yep')

        assert os.path.commonprefix(Ellipsis) == 'yep'

    def testSafeSpy2(self):
        spy2(os.path.exists)

        assert os.path.exists('/Foo') is False

        verify(os.path).exists('/Foo')

    class TestRejections:
        def testA(self):
            with pytest.raises(TypeError) as exc:
                when2(os)
            assert str(exc.value) == "given object '%s' is not a function" % os

            cp = os.path.commonprefix
            with pytest.raises(TypeError) as exc:
                spy2(cp)
            assert str(exc.value) == "can't guess origin of 'cp'"

            ptch = patch
            with pytest.raises(TypeError) as exc:
                ptch(os.path.exists, lambda: 'boo')
            assert str(exc.value) == "could not destructure first argument"

            with pytest.raises(TypeError) as exc:
                when2(
                    os.path.exists)
            assert str(exc.value) == "could not destructure first argument"


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
