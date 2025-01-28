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


Breaking changes in v2
======================

Two functions have been renamed:

- `verifyNoMoreInteractions` is deprecated. Use `ensureNoUnverifiedInteractions` instead.

Although `verifyNoMoreInteractions` is the name used in mockito for Java, it is a misnomer over there
too (imo).  Its docs say "Checks if any of given mocks has any unverified interaction.", and we
make that clear now in the name of the function, so you don't need the docs to tell you what it does.

- `verifyNoUnwantedInteractions` is deprecated. Use `verifyExpectedInteractions` instead.

The new name should make it clear that it corresponds to the usage of `expect` (as alternative to `when`).


Development
===========

I use `rye <https://rye-up.com/>`_, and if you do too: you just clone this repo
to your computer, then run ``rye sync`` in the root directory.  Finally, activate
the virtualenv.  (``rye shell`` gives you a hint on how to do that.)

::

    pytest
