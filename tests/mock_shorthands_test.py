import asyncio
import inspect

import pytest

from mockito import mock, when


pytestmark = pytest.mark.usefixtures("unstub")


class _Action:
    def no_arg(self):
        return None


def run(coro):
    return asyncio.run(coro)


def test_constructor_function_without_params_accepts_any_args():
    cat = mock({"meow": lambda: "Miau!"})

    assert cat.meow() == "Miau!"
    assert cat.meow(1, excited=True) == "Miau!"


def test_zero_arg_constructor_function_still_respects_spec_signature():
    action = mock({"no_arg": lambda: 12}, spec=_Action)

    assert action.no_arg() == 12

    with pytest.raises(TypeError):
        action.no_arg(1)


def test_async_prefix_marks_method_and_uses_default_async_none_answer():
    session = mock({"async get": ...})

    pending = session.get("https://example.com", raise_for_status=True)

    assert inspect.isawaitable(pending)
    assert run(pending) is None


def test_async_prefix_with_zero_arg_function_accepts_any_arguments():
    response = object()
    session = mock({"async get": lambda: response})

    pending = session.get("https://example.com", timeout=1)

    assert inspect.isawaitable(pending)
    assert run(pending) is response


def test_async_prefix_rejects_non_callable_non_ellipsis_value():
    response = object()

    with pytest.raises(TypeError) as exc:
        mock({"async get": response})

    assert str(exc.value) == (
        "Async shorthand 'async get' expects a function value or Ellipsis. "
        "Use `lambda: value` for fixed async return values."
    )


def test_async_marking_survives_followup_when_stubbing():
    session = mock({"async get": ...})
    when(session).get(...).thenReturn("ok")

    pending = session.get("https://example.com")

    assert inspect.isawaitable(pending)
    assert run(pending) == "ok"


def test_enter_ellipsis_installs_standard_enter_and_default_exit():
    resource = mock({"__enter__": ...})

    with resource as entered:
        assert entered is resource

    assert resource.__exit__(None, None, None) is False


async def _use_async_resource(resource):
    async with resource as entered:
        return entered


def test_aenter_ellipsis_installs_standard_aenter_and_default_aexit():
    resource = mock({"__aenter__": ...})

    assert run(_use_async_resource(resource)) is resource

    pending = resource.__aexit__(None, None, None)
    assert inspect.isawaitable(pending)
    assert run(pending) is False


def test_iter_shortcut_wraps_values_in_iterator():
    numbers = mock({"__iter__": [1, 2, 3]})

    assert list(numbers) == [1, 2, 3]


def test_iter_shortcut_normalizes_callable_results():
    numbers = mock({"__iter__": lambda: [1, 2, 3]})

    assert list(numbers) == [1, 2, 3]


async def _collect_async_iter(values):
    seen = []
    async for value in values:
        seen.append(value)
    return seen


def test_aiter_shortcut_wraps_sync_values_in_async_iterator():
    numbers = mock({"__aiter__": [1, 2, 3]})

    assert run(_collect_async_iter(numbers)) == [1, 2, 3]


def test_aiter_shortcut_normalizes_callable_results():
    numbers = mock({"__aiter__": lambda: [4, 5, 6]})

    assert run(_collect_async_iter(numbers)) == [4, 5, 6]
