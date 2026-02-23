from __future__ import annotations
from . import matchers
from .utils import contains_strict

import functools
import inspect

try:
    from inspect import signature, Parameter, Signature
except ImportError:
    from funcsigs import signature, Parameter, Signature  # type: ignore[import-not-found, no-redef]  # noqa: E501


def get_signature(obj: object, method_name: str) -> Signature | None:
    method = getattr(obj, method_name)

    # Eat self for unbound methods bc signature doesn't do it
    if (
        inspect.isclass(obj)
        and not inspect.ismethod(method)
        and not isinstance(obj.__dict__.get(method_name), staticmethod)
    ):
        method = functools.partial(method, None)

    try:
        return signature(method)
    except Exception:
        return None


def match_signature(sig: Signature, args: tuple, kwargs: dict) -> None:
    sig.bind(*args, **kwargs)


def match_signature_allowing_placeholders(  # noqa: C901
    sig: Signature, args: tuple, kwargs: dict
) -> None:
    # Let's face it. If this doesn't work out, we have to do it the hard
    # way and reimplement something like `sig.bind` with our specific
    # need for `...`, `*args`, and `**kwargs` support.

    if args and args[-1] is Ellipsis and not kwargs:
        # Invariant: Ellipsis as the sole argument should just pass, regardless
        # if it actually can consume an arg or the function does not take any
        # arguments at all
        if len(args) == 1:
            return

        has_kwargs = has_var_keyword(sig)
        # Ellipsis is the last arg in args; then it matches all keyword
        # arguments as well. So the strategy here is to strip off all
        # the keyword arguments from the signature, and do a partial
        # bind with the rest.
        params = [p for n, p in sig.parameters.items()
                  if p.kind not in (Parameter.KEYWORD_ONLY,
                                    Parameter.VAR_KEYWORD)]
        sig = sig.replace(parameters=params)
        # Ellipsis should fill at least one argument. We strip it off if
        # it can stand for a `kwargs` argument.
        sig.bind_partial(*(args[:-1] if has_kwargs else args))
    else:
        # `*args` should at least match one arg (t.i. not `*[]`), so we
        # keep it here. The value and its type is irrelevant in python.
        args_provided = contains_strict(args, matchers.ARGS_SENTINEL)

        # If we find the `**kwargs` sentinel we must remove it, bc its
        # name cannot be matched against the sig.
        kwargs_provided = matchers.KWARGS_SENTINEL in kwargs
        if kwargs_provided:
            kwargs = kwargs.copy()
            kwargs.pop(matchers.KWARGS_SENTINEL)


        if args_provided or kwargs_provided:
            try:
                sig.bind(*args, **kwargs)
            except TypeError as e:
                error = str(e)
                if 'too many positional arguments' in error:
                    raise TypeError('no argument for *args left')
                if 'multiple values for argument' in error:
                    raise
                if 'got an unexpected keyword argument' in error:  # PY>3.5
                    raise

            else:
                if kwargs_provided and not has_var_keyword(sig):
                    pos_args = positional_arguments(sig)
                    len_args = len(args) - int(args_provided)
                    len_kwargs = len(kwargs)
                    provided_args = len_args + len_kwargs
                    # Substitute at least one argument for the `**kwargs`,
                    # the user provided; t.i. do not allow kwargs to
                    # satisfy an empty `{}`.
                    if provided_args + 1 > pos_args:
                        raise TypeError(
                            'no keyword argument for **kwargs left')

        else:
            # Without Ellipsis and the other stuff this would really be
            # straight forward.
            sig.bind(*args, **kwargs)


def positional_arguments(sig: Signature) -> int:
    return len([p for n, p in sig.parameters.items()
                if p.kind in (Parameter.POSITIONAL_ONLY,
                              Parameter.POSITIONAL_OR_KEYWORD)])

def has_var_keyword(sig: Signature) -> bool:
    return any(p for n, p in sig.parameters.items()
               if p.kind is Parameter.VAR_KEYWORD)

