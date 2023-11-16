Mockito is a spying framework originally based on `the Java library with the same name
<https://github.com/mockito/mockito>`_.  (Actually *we* invented the strict stubbing mode
back in 2009.)  

.. image:: https://github.com/kaste/mockito-python/actions/workflows/test-lint-go.yml/badge.svg
    :target: https://github.com/kaste/mockito-python/actions/workflows/test-lint-go.yml


Install
=======

``pip install mockito``



Quick Start
===========

90% use case is that you want to stub out a side effect.

::

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




Read the docs
=============

http://mockito-python.readthedocs.io/en/latest/


Run the tests
-------------

::

    pip install pytest
    py.test
