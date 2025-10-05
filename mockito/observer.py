from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar, Generic

T = TypeVar('T', bound='Subject')

class Observer(Generic[T], ABC):

    @abstractmethod
    def update(self, subject: T) -> None:
        pass

class Subject(ABC):

    @abstractmethod
    def attach(self, observer: Observer[T]) -> None:
        pass

    @abstractmethod
    def detach(self, observer: Observer[T]) -> None:
        pass

    @abstractmethod
    def notify(self) -> None:
        pass
