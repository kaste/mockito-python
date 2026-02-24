# Copyright (c) 2008-2016 Szczepan Faber, Serhiy Oplakanets, Herr Kaste
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import annotations
import inspect
import operator
import types
import functools
from collections import deque
from contextlib import contextmanager
from typing import AsyncIterator, Callable, Iterable, Iterator, cast

from . import invocation, signature, utils
from .mock_registry import mock_registry


__all__ = ['mock']

__tracebackhide__ = operator.methodcaller(
    "errisinstance",
    invocation.InvocationError
)
SUPPORTS_MARKCOROUTINEFUNCTION = hasattr(inspect, "markcoroutinefunction")

_MISSING_ATTRIBUTE = object()

_CONFIG_ASYNC_PREFIX = "async "
_ASYNC_BY_PROTOCOL_METHODS = {"__aenter__", "__aexit__", "__anext__"}


class _Dummy:
    # We spell out `__call__` here for convenience. All other magic methods
    # must be configured before use, but we want `mock`s to be callable by
    # default.
    def __call__(self, *args, **kwargs):
        return self.__getattr__('__call__')(*args, **kwargs)  # type: ignore[attr-defined]  # noqa: E501


def remembered_invocation_builder(
    mock: Mock,
    method_name: str,
    discard_first_arg: bool,
    *args,
    **kwargs
):
    invoc = invocation.RememberedInvocation(
        mock, method_name, discard_first_arg=discard_first_arg
    )
    return invoc(*args, **kwargs)


class wait_for_invocation:
    ANSWER_SELECTOR_METHODS = {
        'thenReturn',
        'thenRaise',
        'thenAnswer',
        'thenCallOriginalImplementation',
    }

    def __init__(self, theMock, method_name, **kwargs):
        self.theMock = theMock
        self.method_name = method_name
        self.kwargs = kwargs

    def should_continue_with_stubbed_invocation(
        self,
        value: object,
        allow_classes: bool = False
    ) -> bool:
        if (
            inspect.isfunction(value)
            or inspect.ismethod(value)
            or inspect.isbuiltin(value)
            or isinstance(value, staticmethod)
            or isinstance(value, classmethod)
            or isinstance(value, functools.partialmethod)
            or isinstance(value, types.MethodDescriptorType)
            or isinstance(value, types.WrapperDescriptorType)
            or isinstance(value, types.ClassMethodDescriptorType)
        ):
            return True

        # Generic callable fallback, but keep custom descriptors/property-like
        # attributes on the property stubbing path.
        return (
            callable(value)
            and (allow_classes or not inspect.isclass(value))
            and not hasattr(value, '__get__')
        )

    def __call__(self, *args, **kwargs):
        self.ensure_target_is_callable()
        return invocation.StubbedInvocation(
            self.theMock, self.method_name, **self.kwargs)(*args, **kwargs)

    def ensure_target_is_callable(self) -> None:
        target, was_in_spec = self.theMock._get_original_method_before_stub(
            self.method_name
        )

        # Missing attributes can still be added in loose mode.
        if not was_in_spec and target is None:
            return

        if self.should_continue_with_stubbed_invocation(
            target, allow_classes=True
        ):
            return

        raise invocation.InvocationError("'%s' is not callable." % self.method_name)

    def __getattr__(self, attr_name):
        self.ensure_target_is_not_callable(attr_name)

        if not inspect.isclass(self.theMock.mocked_obj):
            raise invocation.InvocationError(
                "Cannot stub property '%s' on an instance. "
                "Use class-level stubbing instead: "
                "when(%s).%s.thenReturn(...)."
                % (
                    self.method_name,
                    type(self.theMock.mocked_obj).__name__,
                    self.method_name,
                )
            )

        def answer_selector_method(*args, **kwargs):
            # Avoid patching during attribute lookup so that a (faulty)
            # `with when(F).p.thenReturn:` does *not* yet mutate F.
            invoc = invocation.StubbedPropertyAccess(
                self.theMock, self.method_name, **self.kwargs)()
            return getattr(invoc, attr_name)(*args, **kwargs)

        return answer_selector_method

    def ensure_target_is_not_callable(self, attr_name: str) -> None:
        spec = self.theMock.spec
        if spec is None:
            return

        try:
            value = inspect.getattr_static(spec, self.method_name)
        except AttributeError:
            if inspect.isclass(spec):
                try:
                    value = getattr(spec, self.method_name)
                except AttributeError:
                    return
            else:
                return

        if self.should_continue_with_stubbed_invocation(value):
            raise invocation.InvocationError(
                f"expected an invocation of '{self.method_name}'"
            )


class _mocked_property:
    def __init__(self, mock, method_name):
        self.mock = mock
        self.method_name = method_name

    def __get__(self, obj, type):
        # For property/descriptors, `thenCallOriginalImplementation()` must
        # call `original_descriptor.__get__(obj, type)`. Unlike regular method
        # stubs, these `obj/type` binding values are only available during this
        # attribute access path, so we keep them in temporary context.
        with self.mock.property_access_context(self.method_name, obj, type):
            return invocation.RememberedPropertyAccess(
                self.mock, self.method_name)()

    def __set__(self, obj, value):
        # Keep this wrapper a data descriptor so it wins over instance
        # __dict__ during reads.
        return None

    def __delete__(self, obj):
        return None


class Mock:
    def __init__(
        self,
        mocked_obj: object,
        strict: bool = True,
        spec: object | None = None
    ) -> None:
        self.mocked_obj = mocked_obj
        self.strict = strict
        self.spec = spec

        self.invocations: list[invocation.RealInvocation] = []
        self.stubbed_invocations: deque[invocation.StubbedInvocation] = deque()

        self._original_methods: dict[str, object | None] = {}
        self._methods_to_unstub: dict[str, object] = {}
        self._signatures_store: dict[str, signature.Signature | None] = {}
        self._property_access_context: \
            list[tuple[str, object | None, object]] = []

        self._observers: list = []
        self._methods_marked_as_coroutine: set[str] = set()

    def attach(self, observer) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer) -> None:
        try:
            self._observers.remove(observer)
        except ValueError:
            pass

    def remember(self, invocation: invocation.RealInvocation) -> None:
        self.invocations.append(invocation)
        for observer in self._observers:
            observer.update(invocation)

    def finish_stubbing(
        self, stubbed_invocation: invocation.StubbedInvocation
    ) -> None:
        self.stubbed_invocations.appendleft(stubbed_invocation)

    def clear_invocations(self) -> None:
        self.invocations = []

    def get_original_method(self, method_name: str) -> object | None:
        return self._original_methods.get(method_name, None)

    def peek_original_method(self, method_name: str) -> object | None:
        try:
            return self._original_methods[method_name]
        except KeyError:
            original_method, _ = self._get_original_method_before_stub(method_name)
            return original_method

    @contextmanager
    def property_access_context(
        self, method_name: str, obj: object | None, type_: object
    ):
        self._property_access_context.append((method_name, obj, type_))
        try:
            yield
        finally:
            self._property_access_context.pop()

    def get_current_property_access(
        self, method_name: str
    ) -> tuple[object | None, object]:
        for accessed_method_name, obj, type_ in reversed(
            self._property_access_context
        ):
            if accessed_method_name == method_name:
                return obj, type_

        raise RuntimeError(
            "Could not resolve property access context for '%s'."
            % method_name
        )

    # STUBBING

    def _get_original_method_before_stub(
        self, method_name: str
    ) -> tuple[object | None, bool]:
        """
        Looks up the original method on the `spec` object and returns it
        together with an indication of whether the method is found
        "directly" on the `spec` object.

        This is used to decide whether the method should be stored as an
        original_method and should therefore be replaced when unstubbing.
        """
        if self.spec is None:
            return None, False

        try:
            return self.spec.__dict__[method_name], True
        except (AttributeError, KeyError):
            # If the attr is not directly in __dict__, class specs should use
            # static lookup so inherited descriptors are preserved as
            # descriptors (instead of triggering __get__ via getattr).
            if inspect.isclass(self.spec):
                try:
                    return inspect.getattr_static(self.spec, method_name), False
                except AttributeError:
                    # If static lookup misses (e.g. metaclass __getattr__),
                    # fall back to dynamic lookup.
                    pass

            # For instance specs, keep dynamic getattr so existing
            # bound-method/spying behavior stays unchanged.
            return getattr(self.spec, method_name, None), False

    def set_method(self, method_name: str, new_method: object) -> None:
        setattr(self.mocked_obj, method_name, new_method)

    def replace_method(
        self, method_name: str, original_method: object | None
    ) -> None:
        discard_first_arg = self._takes_implicit_self_or_cls(original_method)

        def new_mocked_method(*args, **kwargs):
            return remembered_invocation_builder(
                self, method_name, discard_first_arg, *args, **kwargs
            )

        new_mocked_method.__name__ = method_name
        if original_method:
            new_mocked_method.__doc__ = original_method.__doc__
            new_mocked_method.__wrapped__ = original_method  # type: ignore[attr-defined]
            try:
                new_mocked_method.__module__ = original_method.__module__
            except AttributeError:
                pass

        if (
            _is_coroutine_method(original_method)
            and SUPPORTS_MARKCOROUTINEFUNCTION
        ):
            new_mocked_method = inspect.markcoroutinefunction(new_mocked_method)

        if inspect.ismethod(original_method):
            new_mocked_method = utils.newmethod(new_mocked_method, self.mocked_obj)

        if isinstance(original_method, staticmethod):
            new_mocked_method = staticmethod(new_mocked_method)
        elif isinstance(original_method, classmethod):
            new_mocked_method = classmethod(new_mocked_method)  # type: ignore[assignment]  # noqa: E501
        elif (
            inspect.isclass(self.mocked_obj)
            and inspect.isclass(original_method)  # TBC: Inner classes
        ):
            new_mocked_method = staticmethod(new_mocked_method)

        self.set_method(method_name, new_mocked_method)

    def stub(self, method_name: str) -> None:
        try:
            self._methods_to_unstub[method_name]
        except KeyError:
            (
                original_method,
                was_in_spec
            ) = self._get_original_method_before_stub(method_name)
            if was_in_spec:
                # This indicates the original method was found directly on
                # the spec object and should therefore be restored by unstub
                self._methods_to_unstub[method_name] = original_method
            else:
                self._methods_to_unstub[method_name] = _MISSING_ATTRIBUTE

            self._original_methods[method_name] = original_method
            self.replace_method(method_name, original_method)

    def stub_property(self, method_name: str) -> None:
        try:
            self._methods_to_unstub[method_name]
        except KeyError:
            (
                original_method,
                was_in_spec
            ) = self._get_original_method_before_stub(method_name)

            self._original_methods[method_name] = original_method
            self.set_method(method_name, _mocked_property(self, method_name))

            if was_in_spec:
                # This indicates the original method was found directly on
                # the spec object and should therefore be restored by unstub
                self._methods_to_unstub[method_name] = original_method
            else:
                self._methods_to_unstub[method_name] = _MISSING_ATTRIBUTE


    def forget_stubbed_invocation(
        self, invocation: invocation.StubbedInvocation
    ) -> None:
        assert invocation in self.stubbed_invocations

        if len(self.stubbed_invocations) == 1:
            mock_registry.unstub_mock(self)
            return

        self.stubbed_invocations.remove(invocation)

        if not any(
            inv.method_name == invocation.method_name
            for inv in self.stubbed_invocations
        ):
            original_method = self._methods_to_unstub.pop(
                invocation.method_name
            )
            self.restore_method(invocation.method_name, original_method)

    def restore_method(self, method_name: str, original_method: object) -> None:
        if original_method is _MISSING_ATTRIBUTE:
            delattr(self.mocked_obj, method_name)
        else:
            self.set_method(method_name, original_method)

    def unstub(self) -> None:
        while self._methods_to_unstub:
            method_name, original_method = self._methods_to_unstub.popitem()
            self.restore_method(method_name, original_method)
        self.stubbed_invocations = deque()
        self.invocations = []
        self._methods_marked_as_coroutine = set()

    # SPECCING

    def mark_as_coroutine(self, method_name: str) -> None:
        self._methods_marked_as_coroutine.add(method_name)

    def is_marked_as_coroutine(self, method_name: str) -> bool:
        return method_name in self._methods_marked_as_coroutine

    def has_method(self, method_name: str) -> bool:
        if self.spec is None:
            return True

        return hasattr(self.spec, method_name)

    def get_signature(self, method_name: str) -> signature.Signature | None:
        if self.spec is None:
            return None

        try:
            return self._signatures_store[method_name]
        except KeyError:
            sig = signature.get_signature(self.spec, method_name)
            self._signatures_store[method_name] = sig
            return sig

    def will_have_self_or_cls(self, method_name: str) -> bool:
        original_method = self.peek_original_method(method_name)
        return self._takes_implicit_self_or_cls(original_method)

    def _takes_implicit_self_or_cls(
        self, original_method: object | None
    ) -> bool:
        # If original_method is None, we *added* it to mocked_obj
        # and thus, it will eat self iff mocked_obj is a class.
        return (
            inspect.ismethod(original_method)
            or (
                inspect.isclass(self.mocked_obj)
                and not isinstance(original_method, staticmethod)
                and not inspect.isclass(original_method)
            )
        )


def _is_coroutine_method(method: object | None) -> bool:
    if isinstance(method, (staticmethod, classmethod)):
        method = method.__func__
    elif inspect.ismethod(method):
        method = method.__func__

    return inspect.iscoroutinefunction(method)


class _OMITTED(object):
    def __repr__(self):
        return 'OMITTED'


OMITTED = _OMITTED()

def mock(config_or_spec=None, spec=None, strict=OMITTED):  # noqa: C901
    """Create 'empty' objects ('Mocks').

    Will create an empty unconfigured object, that you can pass
    around. All interactions (method calls) will be recorded and can be
    verified using :func:`verify` et.al.

    A plain `mock()` will be not `strict`, and thus all methods regardless
    of the arguments will return ``None``.

    .. note:: Technically all attributes will return an internal interface.
        Because of that a simple ``if mock().foo:`` will surprisingly pass.

    If you set strict to ``True``: ``mock(strict=True)`` all unexpected
    interactions will raise an error instead.

    You configure a mock using :func:`when`, :func:`when2` or :func:`expect`.
    You can also very conveniently just pass in a dict here::

        response = mock({'text': 'ok', 'raise_for_status': lambda: None})

    You can also create an empty Mock which is specced against a given
    `spec`: ``mock(requests.Response)``. These mock are by default strict,
    thus they raise if you want to stub a method, the spec does not implement.
    Mockito will also match the function signature.

    You can pre-configure a specced mock as well::

        response = mock({'json': lambda: {'status': 'Ok'}},
                        spec=requests.Response)

    Mocks are by default callable. Configure the callable behavior using
    `when`::

        dummy = mock()
        when(dummy).__call__(1).thenReturn(2)

    All other magic methods must be configured this way or they will raise an
    AttributeError.


    See :func:`verify` to verify your interactions after usage.

    """

    if type(config_or_spec) is dict:
        config, spec = config_or_spec, spec
    else:
        config, spec = {}, spec or config_or_spec

    if strict is OMITTED:
        strict = False if spec is None else True


    class Dummy(_Dummy):
        if spec:
            __class__ = spec  # make isinstance work

        def __getattr__(self, method_name):
            if strict:
                __tracebackhide__ = operator.methodcaller(
                    "errisinstance", AttributeError
                )
                # deepcopy catches a possible AttributeError, fallback
                # to an arbitrary RuntimeError
                error_type = (
                    RuntimeError
                    if method_name == '__deepcopy__'
                    else AttributeError
                )
                raise error_type(
                    "'Dummy' has no attribute %r configured" % method_name)

            if (
                method_name != "__call__"
                and method_name == "__{}__".format(method_name[2:-2])
            ):
                raise AttributeError(method_name)

            # If a descriptor exists on the dummy class, resolve it here so
            # InvocationError from descriptor-backed stubs is not converted
            # into a dynamic fallback attribute.
            if method_name != "__call__":
                try:
                    class_attr = inspect.getattr_static(type(self), method_name)
                except AttributeError:
                    pass
                else:
                    if hasattr(class_attr, "__get__"):
                        try:
                            return class_attr.__get__(self, type(self))
                        except AttributeError as error:
                            if isinstance(error, invocation.InvocationError):
                                raise
                            # Keep dynamic-attribute behavior for descriptors that
                            # deliberately signal missing via AttributeError.

            def ad_hoc_function(*args, **kwargs):
                return remembered_invocation_builder(
                    theMock, method_name, False, *args, **kwargs
                )
            ad_hoc_function.__name__ = method_name
            ad_hoc_function.__self__ = obj  # type: ignore[attr-defined]
            if spec:
                try:
                    original_method = getattr(spec, method_name)
                    ad_hoc_function.__wrapped__ = original_method  # type: ignore[attr-defined]  # noqa: E501
                    ad_hoc_function.__doc__ = original_method.__doc__
                except AttributeError:
                    pass

            return ad_hoc_function

        def __repr__(self):
            name = 'Dummy'
            if spec:
                name += spec.__name__
            return "<%s id=%s>" % (name, id(self))


    # That's a tricky one: The object we will return is an *instance* of our
    # Dummy class, but the mock we register will point and patch the class.
    # T.i. so that magic methods (`__call__` etc.) can be configured.
    obj = Dummy()
    theMock = Mock(Dummy, strict=strict, spec=spec)

    normalized_names = {
        _normalize_config_key(raw_name)[0]
        for raw_name in config
    }

    for raw_name, value in config.items():
        _configure_mock_from_shorthand(
            theMock,
            Dummy,
            obj,
            raw_name,
            value,
            normalized_names,
        )

    mock_registry.register(obj, theMock)
    return obj


def _configure_mock_from_shorthand(
    theMock: Mock,
    Dummy: type,
    obj: object,
    raw_name: str,
    value: object,
    configured_names: set[str],
) -> None:
    method_name, marked_async = _normalize_config_key(raw_name)
    should_be_async = marked_async or method_name in _ASYNC_BY_PROTOCOL_METHODS

    if method_name in {"__enter__", "__aenter__"} and value is Ellipsis:
        _stub_from_shorthand(
            theMock,
            method_name,
            return_value=obj,
            force_async=(method_name == "__aenter__"),
        )

        companion_exit = "__aexit__" if method_name == "__aenter__" else "__exit__"
        if companion_exit not in configured_names:
            _stub_from_shorthand(
                theMock,
                companion_exit,
                return_value=False,
                force_async=(companion_exit == "__aexit__"),
            )
        return

    if method_name == "__iter__":
        iter_answer = _normalize_iter_answer(value)
        _stub_from_shorthand(theMock, method_name, answer=iter_answer)
        return

    if method_name == "__aiter__":
        aiter_answer = _normalize_aiter_answer(value)
        _stub_from_shorthand(theMock, method_name, answer=aiter_answer)
        return

    if inspect.isfunction(value):
        function_answer = _widen_zero_arg_callable(value)
        _stub_from_shorthand(
            theMock,
            method_name,
            answer=function_answer,
            force_async=should_be_async,
        )
        return

    if should_be_async:
        if value is Ellipsis:
            _stub_from_shorthand(theMock, method_name, force_async=True)
            return

        raise TypeError(
            "Async shorthand '%s' expects a function value or Ellipsis. "
            "Use `lambda: value` for fixed async return values."
            % raw_name
        )

    setattr(Dummy, method_name, value)


def _normalize_config_key(raw_name: str) -> tuple[str, bool]:
    if raw_name.startswith(_CONFIG_ASYNC_PREFIX):
        return raw_name[len(_CONFIG_ASYNC_PREFIX):], True
    return raw_name, False


def _stub_from_shorthand(
    theMock: Mock,
    method_name: str,
    *,
    answer: object = OMITTED,
    return_value: object = OMITTED,
    force_async: bool = False,
) -> None:
    if force_async:
        theMock.mark_as_coroutine(method_name)

    stubbed = invocation.StubbedInvocation(theMock, method_name)(Ellipsis)

    if answer is not OMITTED:
        stubbed.thenAnswer(answer)  # type: ignore[arg-type]
    elif return_value is not OMITTED:
        stubbed.thenReturn(return_value)


def _widen_zero_arg_callable(function: object):
    if not inspect.isfunction(function):
        return function

    try:
        params = inspect.signature(function).parameters
    except Exception:
        return function

    if params:
        return function

    def widened(*args, **kwargs):
        return function()

    widened.__name__ = function.__name__
    widened.__doc__ = function.__doc__
    return widened


def _normalize_iter_answer(value) -> Callable[..., Iterator[object]]:
    def answer(*args, **kwargs) -> Iterator[object]:
        result = value(*args, **kwargs) if callable(value) else value
        return iter(cast(Iterable[object], result))

    return answer


def _normalize_aiter_answer(value) -> Callable[..., AsyncIterator[object]]:
    def answer(*args, **kwargs) -> AsyncIterator[object]:
        result = value(*args, **kwargs) if callable(value) else value
        return _normalize_aiter_result(result)

    return answer


def _normalize_aiter_result(value) -> AsyncIterator[object]:
    if hasattr(value, "__anext__"):
        return cast(AsyncIterator[object], value)

    aiter = getattr(value, "__aiter__", None)
    if callable(aiter):
        candidate = aiter()
        if hasattr(candidate, "__anext__"):
            return cast(AsyncIterator[object], candidate)
        raise TypeError(
            "__aiter__() must return an async iterator implementing __anext__"
        )

    iterator = iter(cast(Iterable[object], value))

    async def generator() -> AsyncIterator[object]:
        for item in iterator:
            yield item

    return generator()
