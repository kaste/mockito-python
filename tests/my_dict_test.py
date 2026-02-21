
from mockito.mock_registry import IdentityMap


class TestIdentityMap:

    def testSetItemIsImplemented(self):
        td = IdentityMap()
        key = object()
        val = object()
        td[key] = val

    def testGetValueForKey(self):
        td = IdentityMap()
        key = object()
        val = object()
        td[key] = val

        assert td.get(key) == val
        assert td.get(object(), 42) == 42

    def testReplaceValueForSameKey(self):
        td = IdentityMap()
        key = object()
        mock1 = object()
        mock2 = object()
        td[key] = mock1
        td[key] = mock2

        assert td.values() == [mock2]

    def testPopKey(self):
        td = IdentityMap()
        key = object()
        val = object()
        td[key] = val

        assert td.pop(key) == val
        assert td.values() == []

    def testPopValue(self):
        td = IdentityMap()
        key = object()
        val = object()
        td[key] = val

        assert td.pop_value(val) == val
        assert td.values() == []

    def testClear(self):
        td = IdentityMap()
        key = object()
        val = object()
        td[key] = val

        td.clear()
        assert td.values() == []

    def testEqualityIsIgnored(self):
        td = IdentityMap()
        td[{"one", "two", "foo"}] = object()
        td[{"one", "two", "foo"}] = object()
        assert len(td.values()) == 2
