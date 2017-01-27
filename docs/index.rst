.. mockito-python documentation master file, created by
   sphinx-quickstart on Tue Apr 26 14:00:19 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. module:: mockito

Mockito is a spying framework originally based on the Java library with the same name.

.. image:: https://travis-ci.org/kaste/mockito-python.svg?branch=master
    :target: https://travis-ci.org/kaste/mockito-python


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

State-of-the-art, high-five argument matchers::

    # Use the Ellipsis, if you don't care
    when(deferred).defer(...).thenRaise(Timeout)

    # Or **kwargs
    from mockito import kwargs  # alias KWARGS
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


Read
----

.. toctree::
   :maxdepth: 1

   walk-through
   the-functions
   the-matchers
   Changelog <changes>



Report issues, contribute more documentation or give feedback at `Github <https://github.com/kaste/mockito-python>`_!

