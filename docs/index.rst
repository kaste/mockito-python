.. mockito-python documentation master file, created by
   sphinx-quickstart on Tue Apr 26 14:00:19 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. module:: mockito

Mockito is a spying framework originally based on the Java library with the same name.

.. image:: https://github.com/kaste/mockito-python/actions/workflows/test-lint-go.yml/badge.svg
    :target: https://github.com/kaste/mockito-python/actions/workflows/test-lint-go.yml



Install
-------

.. code-block:: python

    pip install mockito

If you already use `pytest`, consider using the plugin `pytest-mockito <https://github.com/kaste/pytest-mockito>`_.


Use
---

.. code-block:: python

    from mockito import when, mock, unstub

    when(os.path).exists('/foo').thenReturn(True)

    # or:
    import requests  # the famous library
    # you actually want to return a Response-like obj, we'll fake it
    response = mock({'status_code': 200, 'text': 'Ok'})
    when(requests).get(...).thenReturn(response)

    # use it
    requests.get('http://google.com/')

    # clean up
    unstub()


Features
--------

Super easy to set up different answers.

::

    # Well, you know the internet
    when(requests).get(...).thenReturn(mock({'status': 501})) \
                           .thenRaise(Timeout("I'm flaky")) \
                           .thenReturn(mock({'status': 200, 'text': 'Ok'}))

State-of-the-art, high-five chaining::

    # SQLAlchemy, fluently
    with when(User).query.filter_by(...).first().thenReturn("A user"):
        assert User.query.filter_by(username='admin').first() == "A user"

State-of-the-art, high-five argument matchers::

    # Use the Ellipsis, if you don't care
    when(deferred).defer(...).thenRaise(Timeout)
    when(requests).get('https://example.com', headers=...)

    # Or **kwargs
    from mockito import kwargs  # or KWARGS
    when(requests).get('http://my-api.com/user', **kwargs)

    # The usual matchers
    from mockito import ANY, or_, not_
    number = or_(ANY(int), ANY(float))
    when(math).sqrt(not_(number)).thenRaise(
        TypeError('argument must be a number'))

No need to `verify` (`assert_called_with`) all the time::

    # Different arguments, different answers
    when(foo).bar(1).thenReturn(2)
    when(foo).bar(2).thenReturn(3)

    # but:
    foo.bar(3)  # throws immediately: unexpected invocation

    # because of that you just know that when
    # you get a `2`, you called it with `1`


Signature checking::

    # when stubbing
    when(requests).get()  # throws immediately: TypeError url required

    # when calling
    request.get(location='http://example.com/')  # TypeError

Property stubbing::

    class Settings:
        @property
        def timeout(self):
            return 10

    with when(Settings).timeout.thenReturn(5):
        assert Settings().timeout == 5


Full async/await support::

    # Avoid internet side effects.
    async def http_get(location: str, session: aiohttp.ClientSession) -> str:
        async with session.get(location, headers=headers, raise_for_status=True) as resp:
            return await resp.text()

    when(module_under_test).http_get('https://example.com', ...).thenReturn('Yep!')


Read
----

.. toctree::
   :maxdepth: 1

   walk-through
   mock-shorthands
   recipes
   the-functions
   any-and-ellipses
   the-matchers
   Changelog <changes>



Report issues, contribute more documentation or give feedback at `Github <https://github.com/kaste/mockito-python>`_!

