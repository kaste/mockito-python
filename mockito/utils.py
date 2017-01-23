
import inspect
import sys
import types


PY3 = sys.version_info >= (3,)


def newmethod(fn, obj):
    if PY3:
        return types.MethodType(fn, obj)
    else:
        return types.MethodType(fn, obj, obj.__class__)


def get_function_host(fn):
    """Destructure a given function into its host and its name

    A host of a function is a module, for methods it is usually its instance
    or its class.

    For all fn: ``getattr(*get_function_host(fn)) == fn``

    Returns tuple (host, fn-name)
    Otherwise should raise TypeError
    """
    try:
        name = fn.__name__
    except AttributeError:
        raise TypeError('given fn %r has no __name__ attribute' % fn)
    else:
        if inspect.ismethod(fn):
            return fn.__self__, name
        elif inspect.isfunction(fn) or inspect.isbuiltin(fn):
            return (inspect.getmodule(fn) or fn.__self__), name
        raise TypeError()

