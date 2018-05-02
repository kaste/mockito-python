.. module:: mockito


The functions
=============

Stable entrypoints are: :func:`when`, :func:`mock`, :func:`unstub`, :func:`verify`, :func:`spy`. Experimental or new function introduces with v1.0.x are: :func:`when2`, :func:`expect`, :func:`verifyNoUnwantedInteractions`, :func:`verifyStubbedInvocationsAreUsed`, :func:`patch`

.. autofunction:: when
.. autofunction:: when2
.. autofunction:: patch
.. autofunction:: expect
.. autofunction:: mock
.. autofunction:: unstub
.. autofunction:: forget_invocations
.. autofunction:: spy
.. autofunction:: spy2

This looks like a plethora of verification functions, and especially since  you often don't need to `verify` at all.

.. autofunction:: verify
.. autofunction:: verifyNoMoreInteractions
.. autofunction:: verifyZeroInteractions
.. autofunction:: verifyNoUnwantedInteractions
.. autofunction:: verifyStubbedInvocationsAreUsed


