import pytest
import mockito
from mockito import mock, when, arg_that

import numpy as np
from . import module


@staticmethod
def xcompare(a, b):
    if isinstance(a, mockito.matchers.Matcher):
        return a.matches(b)

    return np.array_equal(a, b)


# mockito.invocation.MatchingInvocation.compare = xcompare


class TestEnsureNumpyWorks:
    @pytest.mark.xfail
    def testEnsureNumpyArrayAllowedWhenStubbing(self):
        array = np.array([1, 2, 3])
        when(module).one_arg(array).thenReturn('yep')
        assert module.one_arg(array) == 'yep'

    @pytest.mark.xfail
    def testEnsureNumpyArrayAllowedWhenCalling(self):
        array = np.array([1, 2, 3])
        when(module).one_arg(Ellipsis).thenReturn('yep')
        assert module.one_arg(array) == 'yep'

