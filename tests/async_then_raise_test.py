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


def test_when_thenRaise_on_async_method_raises_on_await():
    when(AsyncWorker).run("a").thenRaise(RuntimeError("boom"))

    worker = AsyncWorker()
    pending = worker.run("a")

    assert inspect.isawaitable(pending)
    with pytest.raises(RuntimeError, match="boom"):
        run(pending)


def test_when_thenRaise_on_async_function_raises_on_await():
    this_module = sys.modules[__name__]
    when(this_module).async_job("a").thenRaise(RuntimeError("boom"))

    pending = async_job("a")

    assert inspect.isawaitable(pending)
    with pytest.raises(RuntimeError, match="boom"):
        run(pending)
