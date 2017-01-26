
import importlib
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


def get_obj(path):
    """Return obj for given dotted path.

    Typical inputs for `path` are 'os', 'os.path' in which case you get a
    module; or 'os.path.exists' in which case you get a function from that
    module.

    Returns the given obj in case `path` is not a str. Note: Relative
    imports not supported.

    Raises ImportError or AttributeError as appropriate.

    """
    # Since we usually pass in mocks here; duck typing is not appropriate
    # (mocks respond to every attribute).
    if not isinstance(path, str):
        return path

    if path.startswith('.'):
        raise TypeError('relative imports are not supported')

    parts = path.split('.')
    head, tail = parts[0], parts[1:]

    obj = importlib.import_module(head)

    # Normally a simple reduce, but we go the extra mile
    # for good exception messages.
    for i, name in enumerate(tail):
        try:
            obj = getattr(obj, name)
        except AttributeError:
            # Note the [:i] instead of [:i+1], so we get the path just
            # *before* the AttributeError, t.i. the part of it that went ok.
            module = '.'.join([head] + tail[:i])
            try:
                importlib.import_module(module)
            except ImportError:
                raise AttributeError(
                    "object '%s' has no attribute '%s'" % (module, name))
            else:
                raise AttributeError(
                    "module '%s' has no attribute '%s'" % (module, name))
    return obj

def get_obj_attr_tuple(path):
    """Split path into (obj, attribute) tuple.

    Given `path` is 'os.path.exists' will thus return (os.path, 'exists')

    If path is not a str, delegates to get_function_host(path)

    """
    if not isinstance(path, str):
        return get_function_host(path)

    if path.startswith('.'):
        raise TypeError('relative imports are not supported')

    try:
        leading, end = path.rsplit('.', 1)
    except ValueError:
        raise TypeError('path must have dots')

    return get_obj(leading), end





