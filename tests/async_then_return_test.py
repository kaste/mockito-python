import asyncio
import inspect
import sys

import pytest

from mockito import when


pytestmark = pytest.mark.usefixtures("unstub")


class AsyncWorker:
    async def run(self, task_id):
        return f"real:{task_id}"


async def async_job(task_id):
    return f"real-fn:{task_id}"


def run(coro):
    return asyncio.run(coro)


def test_when_thenReturn_on_async_method_returns_awaitable_result():
    when(AsyncWorker).run("a").thenReturn("stubbed")

    worker = AsyncWorker()
    pending = worker.run("a")

    assert inspect.isawaitable(pending)
    assert run(pending) == "stubbed"


def test_when_thenReturn_on_async_function_returns_awaitable_result():
    this_module = sys.modules[__name__]
    when(this_module).async_job("a").thenReturn("stubbed")

    pending = async_job("a")

    assert inspect.isawaitable(pending)
    assert run(pending) == "stubbed"
