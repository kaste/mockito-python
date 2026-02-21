import asyncio
import inspect
import sys

import pytest

from mockito import patch


pytestmark = pytest.mark.usefixtures("unstub")


class AsyncWorker:
    async def run(self, task_id):
        return f"real:{task_id}"


async def async_job(task_id):
    return f"real-fn:{task_id}"


def run(coro):
    return asyncio.run(coro)


def test_patch_async_bound_method_sync_replacement_returns_awaitable():
    worker = AsyncWorker()
    patch(worker.run, lambda task_id: f"patched:{task_id}")

    pending = worker.run("a")

    assert inspect.isawaitable(pending)
    assert run(pending) == "patched:a"


def test_patch_async_function_sync_replacement_returns_awaitable():
    this_module = sys.modules[__name__]
    patch(this_module.async_job, lambda task_id: f"patched:{task_id}")

    pending = async_job("a")

    assert inspect.isawaitable(pending)
    assert run(pending) == "patched:a"


def test_patch_async_bound_method_sync_replacement_resolves_value():
    worker = AsyncWorker()
    patch(worker.run, lambda task_id: f"patched:{task_id}")

    assert run(worker.run("a")) == "patched:a"


def test_patch_async_function_sync_replacement_resolves_value():
    this_module = sys.modules[__name__]
    patch(this_module.async_job, lambda task_id: f"patched:{task_id}")

    assert run(async_job("a")) == "patched:a"
