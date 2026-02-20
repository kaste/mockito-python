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

from __future__ import annotations
import weakref
from typing import TYPE_CHECKING, Callable, Generic, TypeVar

if TYPE_CHECKING:
    from .mocking import Mock


RegisterObserver = Callable[[object, "Mock"], None]
K = TypeVar("K")
V = TypeVar("V")
T = TypeVar("T")


class MockRegistry:
    """Registry for mocks

    Registers mock()s, ensures that we only have one mock() per mocked_obj, and
    iterates over them to unstub each stubbed method.
    """

    def __init__(self) -> None:
        self.mocks: IdentityMap[object, Mock] = IdentityMap()
        self._register_observers: list[weakref.WeakMethod] = []

    def register(self, obj: object, mock: Mock) -> None:
        self.mocks[obj] = mock

        alive_observers: list[weakref.WeakMethod] = []
        for observer_ref in self._register_observers:
            observer = observer_ref()
            if observer is None:
                continue

            observer(obj, mock)
            alive_observers.append(observer_ref)

        self._register_observers = alive_observers

    def add_register_observer(self, observer: RegisterObserver) -> None:
        self._prune_dead_register_observers()
        for observer_ref in self._register_observers:
            callback = observer_ref()
            if callback is not None and callback == observer:
                return

        self._register_observers.append(weakref.WeakMethod(observer))

    def remove_register_observer(self, observer: RegisterObserver) -> None:
        self._prune_dead_register_observers()

        for i, observer_ref in enumerate(self._register_observers):
            callback = observer_ref()
            if callback is not None and callback == observer:
                del self._register_observers[i]
                break

    def _prune_dead_register_observers(self) -> None:
        self._register_observers = [
            observer_ref
            for observer_ref in self._register_observers
            if observer_ref() is not None
        ]

    def mock_for(self, obj: object) -> Mock | None:
        return self.mocks.get(obj, None)

    def obj_for(self, mock: Mock) -> object | None:
        return self.mocks.lookup(mock)

    def unstub(self, obj: object) -> None:
        try:
            mock = self.mocks.pop(obj)
        except KeyError:
            pass
        else:
            mock.unstub()

    def unstub_mock(self, mock: Mock) -> None:
        self.mocks.pop_value(mock)
        mock.unstub()

    def unstub_all(self) -> None:
        for mock in self.get_registered_mocks():
            mock.unstub()
        self.mocks.clear()

    def get_registered_mocks(self) -> list[Mock]:
        return self.mocks.values()


# We have this dict like because we want non-hashable items in our registry.
class IdentityMap(Generic[K, V]):
    def __init__(self) -> None:
        self._store: list[tuple[K, V]] = []

    def __setitem__(self, key: K, value: V) -> None:
        for i, (k, _) in enumerate(self._store):
            if k is key:
                self._store[i] = (key, value)
                return
        self._store.append((key, value))

    def remove(self, key: K) -> None:
        for i, (k, _) in enumerate(self._store):
            if k is key:
                del self._store[i]
                return

    def pop(self, key: K) -> V:
        for i, (k, value) in enumerate(self._store):
            if k is key:
                del self._store[i]
                return value
        raise KeyError()

    def pop_value(self, value: V) -> V:
        for i, (key, val) in enumerate(self._store):
            if val is value:
                del self._store[i]
                return val
        raise KeyError()

    def get(self, key: K, default: T | None = None) -> V | T | None:
        for k, value in self._store:
            if k is key:
                return value
        return default

    def lookup(self, value: V, default: T | None = None) -> K | T | None:
        for key, v in self._store:
            if v is value:
                return key
        return default

    def values(self) -> list[V]:
        return [v for k, v in self._store]

    def clear(self) -> None:
        self._store[:] = []


mock_registry = MockRegistry()
