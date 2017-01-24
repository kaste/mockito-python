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


Use
---

.. code-block:: python

    from mockito import when, unstub

    when(os.path).exists('/foo').thenReturn(True)

    # or:
    import requests  # the famous library
    # you actually want to return a Response-like obj, we'll fake it
    response = mock({'status_code': 200, 'text': 'Ok'})
    when(requests).get(...).thenReturn(response)

    # use it
    requests.get('http://google.com/')

Read
----

.. toctree::
   :maxdepth: 1

   walk-through
   the-functions
   the-matchers
   Changelog <changes>



Report issues, contribute more documentation or give feedback at `Github <https://github.com/kaste/mockito-python>`_!

