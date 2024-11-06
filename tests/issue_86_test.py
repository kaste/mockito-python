import pytest
from mockito import when


class Data:
    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        if isinstance(other, Data):
            return self.name == other.name
        return NotImplemented

    def tell_name(self):
        return self.name


@pytest.mark.usefixtures('unstub')
class TestIssue86:
    def testValueObjectsAreTreatedByIdentity(self):
        a = Data("Bob")
        b = Data("Bob")
        when(a).tell_name().thenReturn("Sarah")
        when(b).tell_name().thenReturn("Mulder")
        assert a.tell_name() == "Sarah"
        assert b.tell_name() == "Mulder"

