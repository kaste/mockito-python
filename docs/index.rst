.. mockito-python documentation master file, created by
   sphinx-quickstart on Tue Apr 26 14:00:19 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. module:: mockito

Mockito is a spying framework originally based on the Java library with the same name.

.. image:: https://travis-ci.org/kaste/mockito-python.svg?branch=master
    :target: https://travis-ci.org/kaste/mockito-python


Install
=======

``pip install mockito``



Walk-through
============

The 90% use case is that want to stub out a side effect. This is also known as (monkey-)patching. With mockito, it's::

    from mockito import when

    # stub `os.path.exists`
    when(os.path).exists('/foo').thenReturn(True)

    os.path.exists('/foo')  # => True
    os.path.exists('/bar')  # -> throws unexpected invocation

So in difference to traditional patching, in mockito you always specify concrete arguments (a call signature), and its outcome, usually a return value via `thenReturn` or a raised exception via `thenRaise`. That effectively turns function calls into constants for the time of the test.

Do **not** forget to :func:`unstub` of course!

::

    from mockito import unstub
    unstub()  # restore os.path module


Now we mix global module patching with mocks. We want to test the following function using the fab `requests` library::

    import requests

    def get_text(url):
        res = requests.get(url)
        if 200 <= res.status_code < 300:
            return res.text
        return None

How, dare, we did not inject our dependencies! Obviously we can get over that by patching at the module level like before::

    when(requests).get('https://example.com/api').thenReturn(...)

But what should we return? We know it's a `requests.Response` object, (Actually I know this bc I typed this in the ipython REPL first.) But how to construct such a `Response`, its `__init__` doesn't even take any arguments?

Should we actually use a 'real' response object? No, we fake it using :func:`mock`.

::

    # setup
    response = mock({
        'status_code': 200,
        'text': 'Ok'
    }, spec=requests.Response)
    when(requests).get('https://example.com/api').thenReturn(response)

    # run
    assert get_text('https://example.com/api') == 'Ok'

    # done!



Report issues, contribute more documentation or give feedback at `Github <https://github.com/kaste/mockito-python>`_!


The functions
=============

Main entrypoints are: :func:`when`, :func:`when2`, :func:`expect`, :func:`mock`, :func:`unstub`, :func:`verify`, :func:`verifyNoUnwantedInteractions`, :func:`spy`, :func:`patch`

.. autofunction:: when
.. autofunction:: mock
.. autofunction:: verify
.. autofunction:: unstub
.. autofunction:: expect
.. autofunction:: verifyNoUnwantedInteractions
.. autofunction:: when2
.. autofunction:: patch
.. autofunction:: spy



.. The matchers
.. ============

.. .. automodule:: mockito.matchers
..   :members:



Contents:

.. toctree::
   :maxdepth: 2

   nutshell



.. Indices and tables
.. ==================

.. * :ref:`genindex`
.. * :ref:`modindex`
.. * :ref:`search`

