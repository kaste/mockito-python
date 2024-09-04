import pytest
from mockito import when

from . import module


@pytest.mark.usefixtures('unstub')
class TestIssue82:
    def testFunctionWithArgumentNamedValue(self):
        when(module).send(value="test").thenReturn("nope")
        assert module.send(value="test") == "nope"

