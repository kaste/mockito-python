mock() configuration and shorthands
===================================

If you really dig mock driven development, you use dumb mock()s and don't patch
real objects and modules all the time.

The standard setup works as expected::

    cat = mock()
    when(cat).meow().thenReturn("Miau!")

    # Use it
    cat.meow()

To get you up to speed, we have several shortcuts:

    cat = mock({"age": 12})
    cat.age   # => 12

You can also define functions::

    cat = mock({"meow": lambda: "Miau!"})
    cat.meow()  # => "Miau!"

Note that such a lambda without any arguments defined, accepts all possible arguments
and always returns the same answer.  It is thus the same as saying

    when(cat).meow(...).thenReturn("Miau!")  # note the Ellipsis

If you want to define async functions, use

    response = mock({"async text": lambda: "Hi"})
    session = mock({"async get": lambda: response})

To build up a complete `aiohttp` example,

    import aiohttp
    from mockito import when, unstub

    async def fetch_text(location, session):
        async with session.get(location, raise_for_status=True) as resp:
            return await resp.text()

you also need to define the context/with handlers:

    resp = mock({
        "__aenter__": ...,
        "async text": lambda: "Fake!"
    })

    session = mock({
        # since __aenter__ is async by protocol "async __aenter__" is not needed (but allowed)
        "__aenter__": ...,           #  <== ... denotes to install a standard return value of self
                                     #  it always installs a standard __aexit__ returning None or False
                                     #  if not provided by the user

        "async get": lambda: resp,   #  <== install async method with *args, **kwargs
                                     #      equivalent to when(session).get(...).thenReturn(resp)
    })

.. note::

    ``__aenter__``, ``__aexit__``, ``__anext__`` are async by definition,
    use either ``mock({"__aenter__": ...})`` or
    ``mock({"async __aenter__": ...})``.

For ``__aiter__``, we have a special shortcode:

    numbers = mock({"__aiter__": [1, 2, 3]})  # install a function that wraps these values
                                                # in an async iterator for easy use

    async for number in numbers:
        ...


You can also just mark a function async::

    session = mock({
        "__aenter__": ...,
        "async get": ...,            # <==  record the intent that this is an async method
                                     #      and install a `return None` handler as well
                                     # You can override that handler clearly later,
                                     # see right below
    })
    when(session).get(..., raise_for_status=True).thenReturn(resp)  # async! as marked before

# This session can be used as return value for the global constructor, e.g.
when(aiohttp).ClientSession().thenReturn(session)

# and then passed around
body = await fetch_text('https://example.com', session)
assert body == 'Fake!'

We have the same shortcuts available for `__enter__` and `__iter__`.

    mock({"__enter__": ...})  # installs a standard enter that return self
                              # and a standard exit handler returning None if nothing else is
                              # provided by the user.

    mock({"__iter__": [4, 5, 6]})  # install handler and wrap in an iterator

Remember or note that when you rather use specced mock()s you're more or less limited by what the spec
implements.  If you for example use `aiohttp.ClientSession` as the blueprint for your mock,
we already know that `get` is async and you don't need to tell mockito so.

    mock({
        "get": lambda: response   # Look up if ClientSession defines "async def get"
                                  # and follow suit.
    } , spec=ClientSession)
