Mockito is a spying framework originally based on the Java library with the same name.

.. image:: https://travis-ci.org/kaste/mockito-python.svg?branch=master
    :target: https://travis-ci.org/kaste/mockito-python


Install
=======

``pip install mockito``


Run the tests
-------------

::

    pip install pytest
    py.test


Quick Start
===========

90% use case is that you want to stub out a side effect.

::

    from mockito import when, unstub

    when(os.path).exists('/foo').thenReturn(True)

    # or:
    import requests  # the famous library
    # you actually want to return a Response-like obj, we'll fake it
    response = mock({'status_code': 200, 'text': 'Ok'})
    when(requests).get(...).thenReturn(response)

    # use it
    requests.get('http://google.com/')




Read the docs
=============

http://mockito-python.readthedocs.io/en/latest/


