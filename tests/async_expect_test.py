import asyncio
import inspect

import pytest

from mockito import expect, verifyExpectedInteractions
from mockito.invocation import InvocationError
from mockito.verification import VerificationError


pytestmark = pytest.mark.usefixtures("unstub")


class AsyncWorker:
    async def run(self, task_id):
        return f"real:{task_id}"


def run(coro):
    return asyncio.run(coro)


def test_expect_times_async_method_passes_and_verifies():
    worker = AsyncWorker()
    expect(worker, times=1).run("a").thenReturn("stubbed")

    pending = worker.run("a")

    assert inspect.isawaitable(pending)
    assert run(pending) == "stubbed"

    verifyExpectedInteractions(worker)


def test_expect_times_async_method_fails_when_called_too_often():
    worker = AsyncWorker()
    expect(worker, times=1).run("a").thenReturn("stubbed")

    assert run(worker.run("a")) == "stubbed"

    with pytest.raises(InvocationError, match="Wanted times: 1, actual times: 2"):
        worker.run("a")


def test_expect_times_async_method_fails_verification_when_under_called():
    worker = AsyncWorker()
    expect(worker, times=2).run("a").thenReturn("stubbed")

    assert run(worker.run("a")) == "stubbed"

    with pytest.raises(VerificationError, match="Wanted times: 2, actual times: 1"):
        verifyExpectedInteractions(worker)
