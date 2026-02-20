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


async def answer_async(task_id):
    return f"answer-async:{task_id}"


async def answer_async_raises(task_id):
    raise RuntimeError(f"boom:{task_id}")


class AsyncCallableAnswer:
    async def __call__(self, task_id):
        return f"answer-async-callable:{task_id}"


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


def test_when_thenAnswer_async_callable_async_method_returns_awaitable():
    when(AsyncWorker).run("a").thenAnswer(answer_async)

    worker = AsyncWorker()
    pending = worker.run("a")

    assert inspect.isawaitable(pending)
    assert run(pending) == "answer-async:a"


def test_when_thenAnswer_async_callable_async_function_returns_awaitable():
    this_module = sys.modules[__name__]
    when(this_module).async_job("a").thenAnswer(answer_async)

    pending = async_job("a")

    assert inspect.isawaitable(pending)
    assert run(pending) == "answer-async:a"


def test_when_thenAnswer_async_callable_async_method_raises_on_await():
    when(AsyncWorker).run("a").thenAnswer(answer_async_raises)

    worker = AsyncWorker()
    pending = worker.run("a")

    assert inspect.isawaitable(pending)
    with pytest.raises(RuntimeError, match="boom:a"):
        run(pending)


def test_when_thenAnswer_sync_callable_method_returning_awaitable_is_not_auto_awaited():
    when(AsyncWorker).run("a").thenAnswer(lambda task_id: answer_async(task_id))

    worker = AsyncWorker()
    pending = worker.run("a")

    assert inspect.isawaitable(pending)
    returned_awaitable = run(pending)
    assert inspect.isawaitable(returned_awaitable)
    assert run(returned_awaitable) == "answer-async:a"


def test_when_thenAnswer_sync_function_returning_awaitable_is_not_auto_awaited():
    this_module = sys.modules[__name__]
    when(this_module).async_job("a").thenAnswer(lambda task_id: answer_async(task_id))

    pending = async_job("a")

    assert inspect.isawaitable(pending)
    returned_awaitable = run(pending)
    assert inspect.isawaitable(returned_awaitable)
    assert run(returned_awaitable) == "answer-async:a"


def test_when_thenAnswer_async_callable_instance_async_method_resolves_value():
    when(AsyncWorker).run("a").thenAnswer(AsyncCallableAnswer())

    worker = AsyncWorker()
    pending = worker.run("a")

    assert inspect.isawaitable(pending)
    assert run(pending) == "answer-async-callable:a"
