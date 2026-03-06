import pytest

from mockito import (
    ArgumentError,
    ensureNoUnverifiedInteractions,
    mock,
    patch_attr,
    unstub,
    verify,
    when,
)


class Dog(object):
    def waggle(self):
        return 'Unsure'

    def bark(self, sound='Wuff'):
        return sound


class AttrHolder(object):
    value = None


class TestUntub:
    def testIndependentUnstubbing(self):
        rex = Dog()
        mox = Dog()

        when(rex).waggle().thenReturn('Yup')
        when(mox).waggle().thenReturn('Nope')

        assert rex.waggle() == 'Yup'
        assert mox.waggle() == 'Nope'

        unstub(rex)

        assert rex.waggle() == 'Unsure'
        assert mox.waggle() == 'Nope'

        unstub(mox)

        assert mox.waggle() == 'Unsure'

    def testUnconfigureMock(self):
        m = mock()
        when(m).foo().thenReturn(42)
        assert m.foo() == 42
        unstub(m)
        assert m.foo() is None

    def testPartialUnstubByMethodReference(self):
        cat = mock(strict=True)

        when(cat).meow().thenReturn('Miau')
        when(cat).runs().thenReturn('Yip')

        unstub(cat.meow)

        with pytest.raises(AttributeError):
            cat.meow()

        assert cat.runs() == 'Yip'

    def testPartialUnstubByMethodReferenceKeepsDetachedChainAlive(self):
        cat = mock(strict=True)

        when(cat).meow().purr().sleep().thenReturn("ok")
        child = cat.meow()
        grand = child.purr()

        unstub(cat.meow)

        with pytest.raises(AttributeError):
            cat.meow()

        assert grand.sleep() == "ok"

    def testPartialUnstubByMethodReferenceForgetsMethodInvocations(self):
        cat = mock()

        when(cat).meow().thenReturn("Miau")
        when(cat).runs().thenReturn("Yip")

        cat.meow()
        cat.runs()
        verify(cat).runs()

        unstub(cat.meow)

        ensureNoUnverifiedInteractions(cat)

    def testPartialUnstubByMethodReferenceDoesNotRestoreMatchingPatchAttr(self):
        cat = mock(strict=True)
        holder = AttrHolder()

        when(cat).meow().thenReturn("Miau")
        replacement = cat.meow
        patch_attr(holder, "value", replacement)

        assert holder.value is replacement

        unstub(cat.meow)

        assert holder.value is replacement
        with pytest.raises(AttributeError):
            cat.meow()

    @pytest.mark.xfail(
        strict=False,
        reason=(
            "Characterization only: detached bound-method aliases currently "
            "prefer patch_attr replacement matching before method-level unstub "
            "resolution. This may change."
        ),
    )
    def testCurrentBehaviorMethodAliasCanUnpatchWithoutUnstubbingMethod(self):
        cat = mock(strict=True)
        holder = AttrHolder()

        when(cat).meow().thenReturn("Miau")
        replacement = cat.meow
        patch_attr(holder, "value", replacement)

        assert holder.value is replacement

        unstub(replacement)

        assert holder.value is None
        assert cat.meow() == "Miau"


class TestContextManagerUnstubStrategy:

    def testWith1(self):
        rex = Dog()

        with when(rex).waggle().thenReturn('Yup'):
            assert rex.waggle() == 'Yup'
            verify(rex).waggle()

        assert rex.waggle() == 'Unsure'

    def testWith2(self):
        # Ensure the short version to return None works
        rex = Dog()

        with when(rex).waggle():
            assert rex.waggle() is None
            verify(rex).waggle()

        assert rex.waggle() == 'Unsure'

    def testWithRaisingSideeffect(self):
        rex = Dog()

        with pytest.raises(RuntimeError):
            with when(rex).waggle().thenRaise(RuntimeError('Nope')):
                rex.waggle()
            assert rex.waggle() == 'Unsure'

    def testNesting(self):
        # That's not a real test, I just wanted to see how it would
        # look like; bc you run out of space pretty quickly
        rex = Dog()
        mox = Dog()

        with when(rex).waggle().thenReturn('Yup'):
            with when(mox).waggle().thenReturn('Nope'):
                assert rex.waggle() == 'Yup'
                assert mox.waggle() == 'Nope'

        assert rex.waggle() == 'Unsure'
        assert mox.waggle() == 'Unsure'
        # though that's a good looking option
        with when(rex).waggle().thenReturn('Yup'), \
             when(mox).waggle().thenReturn('Nope'):  # noqa: E127
            assert rex.waggle() == 'Yup'
            assert mox.waggle() == 'Nope'

        assert rex.waggle() == 'Unsure'
        assert mox.waggle() == 'Unsure'

    def testOnlyUnstubTheExactStub(self):
        rex = Dog()

        when(rex).bark('Shhh').thenReturn('Nope')
        with when(rex).bark('Miau').thenReturn('Grrr'):
            assert rex.bark('Miau') == 'Grrr'

        assert rex.bark('Shhh') == 'Nope'
        verify(rex, times=2).bark(Ellipsis)

    def testOnlyUnstubTheExcatMethod(self):
        rex = Dog()

        when(rex).bark('Shhh').thenReturn('Nope')
        with when(rex).waggle().thenReturn('Yup'):
            assert rex.waggle() == 'Yup'

        assert rex.bark('Shhh') == 'Nope'
        verify(rex, times=1).bark(Ellipsis)
        verify(rex, times=1).waggle()

    def testCleanupRegistryAfterLastStub(self):
        rex = Dog()

        with when(rex).bark('Shhh').thenReturn('Nope'):
            with when(rex).bark('Miau').thenReturn('Grrr'):
                assert rex.bark('Miau') == 'Grrr'
            assert rex.bark('Shhh') == 'Nope'

        with pytest.raises(ArgumentError):
            verify(rex).bark(Ellipsis)


    class TestEnsureCleanUnstubIfMockingAGlobal:
        def testA(self):
            with when(Dog).waggle().thenReturn('Sure'):
                rex = Dog()
                assert rex.waggle() == 'Sure'

                verify(Dog).waggle()

        def testB(self):
            with when(Dog).waggle().thenReturn('Sure'):
                rex = Dog()
                assert rex.waggle() == 'Sure'

                verify(Dog).waggle()

