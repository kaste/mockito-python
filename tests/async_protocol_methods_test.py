import asyncio
import inspect

import pytest

from mockito import mock, when


pytestmark = pytest.mark.usefixtures("unstub")


def run(coro):
    return asyncio.run(coro)


async def _use_async_resource(resource):
    async with resource as entered:
        return entered


async def _collect_async_iter(values):
    seen = []
    async for value in values:
        seen.append(value)
    return seen


def test_when_thenReturn_on_ad_hoc_mock_aenter_and_aexit_are_awaitable():
    resource = mock()
    when(resource).__aenter__().thenReturn(resource)
    when(resource).__aexit__(..., ..., ...).thenReturn(False)

    pending_enter = resource.__aenter__()
    assert inspect.isawaitable(pending_enter)
    assert run(pending_enter) is resource

    pending_exit = resource.__aexit__(None, None, None)
    assert inspect.isawaitable(pending_exit)
    assert run(pending_exit) is False


def test_when_thenReturn_on_ad_hoc_mock_supports_async_with():
    resource = mock()
    entered = object()
    when(resource).__aenter__().thenReturn(entered)
    when(resource).__aexit__(..., ..., ...).thenReturn(False)

    assert run(_use_async_resource(resource)) is entered


def test_when_thenReturn_on_ad_hoc_mock_anext_is_awaitable():
    values = mock()
    when(values).__anext__().thenReturn(1)

    pending = values.__anext__()
    assert inspect.isawaitable(pending)
    assert run(pending) == 1


def test_when_thenReturn_on_ad_hoc_mock_supports_async_for():
    values = mock()
    when(values).__aiter__().thenReturn(values)
    when(values).__anext__().thenReturn(1).thenReturn(2).thenRaise(StopAsyncIteration)

    assert run(_collect_async_iter(values)) == [1, 2]
