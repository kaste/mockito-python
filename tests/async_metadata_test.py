import inspect
import sys

import pytest

from mockito import expect, patch, when, when2


pytestmark = pytest.mark.usefixtures("unstub")
SUPPORTS_MARKCOROUTINEFUNCTION = hasattr(inspect, "markcoroutinefunction")


def assert_coroutine_metadata_after_stubbing(callable_obj):
    assert (
        inspect.iscoroutinefunction(callable_obj)
        == SUPPORTS_MARKCOROUTINEFUNCTION
    )


class AsyncWorker:
    async def run(self, task_id):
        return f"real:{task_id}"


async def async_job(task_id):
    return f"real-fn:{task_id}"


def test_when_preserves_coroutine_metadata_for_async_class_method():
    worker = AsyncWorker()

    assert inspect.iscoroutinefunction(AsyncWorker.run)
    assert inspect.iscoroutinefunction(worker.run)

    when(AsyncWorker).run("a").thenReturn("stubbed")

    assert_coroutine_metadata_after_stubbing(AsyncWorker.run)
    assert_coroutine_metadata_after_stubbing(worker.run)


def test_when_preserves_coroutine_metadata_for_async_function():
    this_module = sys.modules[__name__]

    assert inspect.iscoroutinefunction(async_job)

    when(this_module).async_job("a").thenReturn("stubbed")

    assert_coroutine_metadata_after_stubbing(async_job)


def test_when_preserves_coroutine_metadata_for_async_bound_method():
    worker = AsyncWorker()

    assert inspect.iscoroutinefunction(worker.run)

    when(worker).run("a").thenReturn("stubbed")

    assert_coroutine_metadata_after_stubbing(worker.run)


def test_when2_preserves_coroutine_metadata_for_async_bound_method():
    worker = AsyncWorker()

    assert inspect.iscoroutinefunction(worker.run)

    when2(worker.run, "a").thenReturn("stubbed")

    assert_coroutine_metadata_after_stubbing(worker.run)


def test_when2_preserves_coroutine_metadata_for_async_function():
    this_module = sys.modules[__name__]

    assert inspect.iscoroutinefunction(async_job)

    when2(this_module.async_job, "a").thenReturn("stubbed")

    assert_coroutine_metadata_after_stubbing(async_job)


def test_expect_preserves_coroutine_metadata_for_async_bound_method():
    worker = AsyncWorker()

    assert inspect.iscoroutinefunction(worker.run)

    expect(worker, times=1).run("a").thenReturn("stubbed")

    assert_coroutine_metadata_after_stubbing(worker.run)


def test_expect_preserves_coroutine_metadata_for_async_function():
    this_module = sys.modules[__name__]

    assert inspect.iscoroutinefunction(async_job)

    expect(this_module, times=1).async_job("a").thenReturn("stubbed")

    assert_coroutine_metadata_after_stubbing(async_job)


def test_patch_preserves_coroutine_metadata_for_async_bound_method():
    worker = AsyncWorker()

    assert inspect.iscoroutinefunction(worker.run)

    patch(worker.run, lambda task_id: f"patched:{task_id}")

    assert_coroutine_metadata_after_stubbing(worker.run)


def test_patch_preserves_coroutine_metadata_for_async_function():
    this_module = sys.modules[__name__]

    assert inspect.iscoroutinefunction(async_job)

    patch(this_module.async_job, lambda task_id: f"patched:{task_id}")

    assert_coroutine_metadata_after_stubbing(async_job)


@pytest.mark.skipif(
    not SUPPORTS_MARKCOROUTINEFUNCTION,
    reason="inspect.markcoroutinefunction is unavailable before Python 3.12",
)
def test_marked_coroutine_then_call_original_returns_sync_value():
    class MarkedAsyncWorker:
        def run(self, task_id):
            return f"real:{task_id}"

    MarkedAsyncWorker.run = inspect.markcoroutinefunction(
        MarkedAsyncWorker.run
    )

    worker = MarkedAsyncWorker()
    assert inspect.iscoroutinefunction(worker.run)

    when(MarkedAsyncWorker).run("a").thenCallOriginalImplementation()

    assert worker.run("a") == "real:a"
