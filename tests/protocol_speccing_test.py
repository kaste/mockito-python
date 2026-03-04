import asyncio
import inspect
from typing import Protocol

import pytest

from mockito import mock, when
from mockito.invocation import InvocationError


pytestmark = pytest.mark.usefixtures("unstub")


def run(coro):
    return asyncio.run(coro)


class ServiceProtocol(Protocol):
    async def fetch(self, path: str, timeout: int = 1) -> str:
        ...

    def close(self, hard: bool = False) -> bool:
        ...


class BaseRunnerProtocol(Protocol):
    def run(self, value: int) -> int:
        ...


class ExtendedRunnerProtocol(BaseRunnerProtocol, Protocol):
    def run(self, value: int, mode: str = "safe") -> int:
        ...


def test_protocol_spec_enforces_method_existence():
    service = mock(ServiceProtocol)

    with pytest.raises(InvocationError):
        when(service).unknown()

    with pytest.raises(AttributeError):
        service.unknown()


def test_protocol_spec_keeps_async_and_sync_methods_distinct():
    service = mock(ServiceProtocol)

    when(service).fetch("/health", timeout=1).thenReturn("ok")
    when(service).close(hard=False).thenReturn(True)

    pending = service.fetch("/health", timeout=1)
    assert inspect.isawaitable(pending)
    assert run(pending) == "ok"

    result = service.close(hard=False)
    assert not inspect.isawaitable(result)
    assert result is True


def test_protocol_spec_enforces_method_signatures_for_stubbing_and_calls():
    service = mock(ServiceProtocol)

    with pytest.raises(TypeError):
        when(service).fetch()

    with pytest.raises(TypeError):
        when(service).close(True, False)

    when(service).close().thenReturn(True)

    with pytest.raises(TypeError):
        service.close(True, False)


def test_protocol_signature_follows_override_definition_on_child_protocol():
    runner = mock(ExtendedRunnerProtocol)

    when(runner).run(1, mode="fast").thenReturn(2)
    assert runner.run(1, mode="fast") == 2

    with pytest.raises(TypeError):
        when(runner).run(1, "fast", "extra")
