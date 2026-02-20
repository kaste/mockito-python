import pytest
from mockito import expect, when, VerificationError
from mockito.invocation import InvocationError


class Dog(object):
    def waggle(self):
        return 'Unsure'

    def bark(self, sound='Wuff'):
        return sound


class TestContextManagerExitStrategyForExpect:
    def testExpectWithDefaultPassesIfUsed(self):
        rex = Dog()
        with expect(rex).waggle().thenReturn('Yup'):
            assert rex.waggle() == 'Yup'

    def testExpectWithDefaultScreamsIfUnused(self):
        rex = Dog()
        with pytest.raises(VerificationError):
            with expect(rex).waggle().thenReturn('Yup'):
                pass

    def testUseEnvSwitchToBypassUsageCheck(self, monkeypatch):
        monkeypatch.setenv("MOCKITO_CONTEXT_MANAGERS_CHECK_USAGE", "0")
        rex = Dog()
        with expect(rex).waggle().thenReturn('Yup'):
            pass

    def testEnvSwitchDoesNotBypassExplicitExpectation(self, monkeypatch):
        monkeypatch.setenv("MOCKITO_CONTEXT_MANAGERS_CHECK_USAGE", "0")
        rex = Dog()
        with pytest.raises(VerificationError):
            with expect(rex, times=1).waggle().thenReturn('Yup'):
                pass

    def testScreamIfUnderUsed(self):
        rex = Dog()
        with pytest.raises(VerificationError):
            with expect(rex, times=2).waggle().thenReturn('Yup'):
                rex.waggle()

    def testUnderUsedExpectationErrorStillUnstubs(self):
        rex = Dog()
        with pytest.raises(VerificationError):
            with expect(rex, times=2).waggle().thenReturn('Yup'):
                rex.waggle()
        assert rex.waggle() == 'Unsure'

    def testScreamIfOverUsed(self):
        rex = Dog()
        with pytest.raises(InvocationError):
            with expect(rex, times=1).waggle().thenReturn('Yup'):
                rex.waggle()
                rex.waggle()


class TestContextManagerExitStrategyForWhen:
    def testScreamIfUnusedByDefault(self):
        rex = Dog()
        with pytest.raises(VerificationError):
            with when(rex).waggle().thenReturn('Yup'):
                pass

    def testUnusedStubErrorStillUnstubs(self):
        rex = Dog()
        with pytest.raises(VerificationError):
            with when(rex).waggle().thenReturn('Yup'):
                pass
        assert rex.waggle() == 'Unsure'

    def testUseEnvSwitchToBypassUsageCheck(self, monkeypatch):
        monkeypatch.setenv("MOCKITO_CONTEXT_MANAGERS_CHECK_USAGE", "0")
        rex = Dog()
        with when(rex).waggle().thenReturn('Yup'):
            pass
