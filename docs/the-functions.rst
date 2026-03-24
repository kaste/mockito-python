.. module:: mockito


The functions
=============

Stable entrypoints are: :func:`when`, :func:`expect`, :func:`mock`, :func:`unstub`,
:func:`verify`, :func:`spy`.
New function introduced in v1 are: :func:`when2`, :func:`verifyExpectedInteractions`, :func:`verifyStubbedInvocationsAreUsed`, :func:`patch`.
New function introduced in v2 are: :func:`patch_attr`, :func:`patch_dict`

.. autofunction:: when
.. autofunction:: expect
.. autofunction:: mock
.. autofunction:: patch
.. autofunction:: patch_attr
.. autofunction:: patch_dict
.. autofunction:: unstub
.. autofunction:: forget_invocations
.. autofunction:: spy
.. autofunction:: spy2
.. autofunction:: when2

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
