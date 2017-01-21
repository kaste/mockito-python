
import inspect

def get_function_host(fn):
    """Destructure a given function into its host, its name and itself

    A host of a function is a module, for methods it is usually its instance
    or its class.

    Returns triple (host, fn-name, fn)
    Otherwise should raise TypeError
    """
    # Note(herrkaste): that is foo code to me. I have no idea of the underlying
    # principles. If someone sees this and knows better, see you on GitHub
    try:
        name = fn.__name__
    except AttributeError:
        pass
    else:
        if inspect.ismethod(fn):
            return fn.__self__, name, fn
        elif inspect.isfunction(fn) or inspect.isbuiltin(fn):
            return (inspect.getmodule(fn) or fn.__self__), name, fn
        raise TypeError()

