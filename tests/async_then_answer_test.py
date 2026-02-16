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


def test_when_thenAnswer_sync_callable_async_method_returns_awaitable():
    when(AsyncWorker).run("a").thenAnswer(
        lambda task_id: f"answer:{task_id}"
    )

    worker = AsyncWorker()
    pending = worker.run("a")

    assert inspect.isawaitable(pending)
    assert run(pending) == "answer:a"


def test_when_thenAnswer_sync_callable_async_function_returns_awaitable():
    this_module = sys.modules[__name__]
    when(this_module).async_job("a").thenAnswer(
        lambda task_id: f"answer:{task_id}"
    )

    pending = async_job("a")

    assert inspect.isawaitable(pending)
    assert run(pending) == "answer:a"
