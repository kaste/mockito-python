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
from collections import deque

from . import invocation, signature, utils
from .mock_registry import mock_registry

from typing import Callable, TypeVar

__all__ = ['mock']

__tracebackhide__ = operator.methodcaller(
    "errisinstance",
    invocation.InvocationError
)

from typing import List

from .observer import Subject, Observer


T = TypeVar('T', bound='Subject')

class _Dummy:
    # We spell out `__call__` here for convenience. All other magic methods
    # must be configured before use, but we want `mock`s to be callable by
    # default.
    def __call__(self, *args, **kwargs):
        return self.__getattr__('__call__')(*args, **kwargs)  # type: ignore[attr-defined]  # noqa: E501


def remembered_invocation_builder(
    mock: Mock, method_name: str, *args, **kwargs
):
    invoc = invocation.RememberedInvocation(mock, method_name)
    return invoc(*args, **kwargs)


class Mock(Subject):
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

        self._original_methods: dict[str, Callable | None] = {}
        self._methods_to_unstub: dict[str, Callable | None] = {}
        self._signatures_store: dict[str, signature.Signature | None] = {}

        self._observers: List[Observer] = []

    def attach(self, observer: Observer[T]) -> None:
        self._observers.append(observer)

    def detach(self, observer: Observer[T]) -> None:
        self._observers.remove(observer)

    def notify(self) -> None:
        for observer in self._observers:
            observer.update(self)

    def remember(self, invocation: invocation.RealInvocation) -> None:
        self.invocations.append(invocation)
        self.notify()

    def finish_stubbing(
        self, stubbed_invocation: invocation.StubbedInvocation
    ) -> None:
        self.stubbed_invocations.appendleft(stubbed_invocation)

    def clear_invocations(self) -> None:
        self.invocations = []

    def get_original_method(self, method_name: str) -> Callable | None:
        return self._original_methods.get(method_name, None)

    # STUBBING

    def _get_original_method_before_stub(
        self, method_name: str
    ) -> tuple[Callable | None, bool]:
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
            # Classes with defined `__slots__` and then no `__dict__` are not
            # patchable but if we catch the `AttributeError` here, we get
            # the better error message for the user.
            return getattr(self.spec, method_name, None), False

    def set_method(self, method_name: str, new_method: object) -> None:
        setattr(self.mocked_obj, method_name, new_method)

    def replace_method(
        self, method_name: str, original_method: object | None
    ) -> None:

        def new_mocked_method(*args, **kwargs):
            return remembered_invocation_builder(
                self, method_name, *args, **kwargs)

        new_mocked_method.__name__ = method_name
        if original_method:
            new_mocked_method.__doc__ = original_method.__doc__
            new_mocked_method.__wrapped__ = original_method  # type: ignore[attr-defined]  # noqa: E501
            try:
                new_mocked_method.__module__ = original_method.__module__
            except AttributeError:
                pass

        if inspect.ismethod(original_method):
            new_mocked_method = utils.newmethod(
                new_mocked_method, self.mocked_obj
            )

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
                self._methods_to_unstub[method_name] = None

            self._original_methods[method_name] = original_method
            self.replace_method(method_name, original_method)

    def forget_stubbed_invocation(
        self, invocation: invocation.StubbedInvocation
    ) -> None:
        assert invocation in self.stubbed_invocations

        if len(self.stubbed_invocations) == 1:
            mock_registry.unstub(self.mocked_obj)
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

    def restore_method(
        self, method_name: str, original_method: object | None
    ) -> None:
        # If original_method is None, we *added* it to mocked_obj, so we
        # must delete it here.
        if original_method:
            self.set_method(method_name, original_method)
        else:
            delattr(self.mocked_obj, method_name)

    def unstub(self) -> None:
        while self._methods_to_unstub:
            method_name, original_method = self._methods_to_unstub.popitem()
            self.restore_method(method_name, original_method)
        self.stubbed_invocations = deque()
        self.invocations = []

    # SPECCING

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

    def eat_self(self, method_name: str) -> bool:
        """Returns if the method will have a prepended self/class arg on call
        """
        try:
            original_method = self._original_methods[method_name]
        except KeyError:
            return False
        else:
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

    def __str__(self):
        name: str = 'Dummy'
        if self.spec:
            name = self.spec.__name__
        return f"Mock<{name}>"


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

            def ad_hoc_function(*args, **kwargs):
                return remembered_invocation_builder(
                    theMock, method_name, *args, **kwargs)
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

        def __str__(self):
            name = 'Dummy'
            if spec:
                name = spec.__name__
            return f"Mock<{name}>"


    # That's a tricky one: The object we will return is an *instance* of our
    # Dummy class, but the mock we register will point and patch the class.
    # T.i. so that magic methods (`__call__` etc.) can be configured.
    obj = Dummy()
    theMock = Mock(Dummy, strict=strict, spec=spec)

    for n, v in config.items():
        if inspect.isfunction(v):
            invocation.StubbedInvocation(theMock, n)(Ellipsis).thenAnswer(v)
        else:
            setattr(Dummy, n, v)

    mock_registry.register(obj, theMock)
    return obj
