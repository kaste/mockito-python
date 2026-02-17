.. module:: mockito


The functions
=============

Stable entrypoints are: :func:`when`, :func:`mock`, :func:`unstub`, :func:`verify`, :func:`spy`. New function introduced in v1 are: :func:`when2`, :func:`expect`, :func:`verifyExpectedInteractions`, :func:`verifyStubbedInvocationsAreUsed`, :func:`patch`

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
.. autofunction:: verifyZeroInteractions
.. autofunction:: verifyExpectedInteractions

In-order verification across one or multiple observed objects is provided by
:class:`InOrder`.

.. autoclass:: InOrder
   :class-doc-from: class

Note that `verifyExpectedInteractions` was named `verifyNoUnwantedInteractions` in v1.
The usage of `verifyNoUnwantedInteractions` is deprecated.

.. autofunction:: verifyStubbedInvocationsAreUsed
.. autofunction:: ensureNoUnverifiedInteractions

Note that `ensureNoUnverifiedInteractions` was named `verifyNoMoreInteractions` in v1.
The usage of `verifyNoMoreInteractions` is deprecated.
