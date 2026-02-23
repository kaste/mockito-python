Any markers and ellipses
=========================

Let's look at how the Ellipsis marker (`...`) works in mockito.

Assume:

::

    class C:
        def function(self, one, two):
            ...

Given

::

    when(C).function(...)

The sole `...` denotes a "whatever" matcher.

These are allowed:

::

    function(1, 2)
    function("1", 2)

But the real function signature still applies. So for `function(one, two)`, these raise:

::

    function()         # raises
    function(1, 2, 3)  # raises

When configured as:

::

    when(C).function(2, ...)

The trailing `...` denotes a rest matcher. We match up to the `2`; the rest is accepted.

::

    function(2, 2)
    function(2, "22")
    function(2, True)

`function(2, 3, 4)` still raises for fixed arity signatures.

The rest matcher also works with variadics:

::

    def function(one, *args, **kwargs): ...

    when(C).function(1, ...)

Allows:

::

    function(1)
    function(1, 2)
    function(1, 2, 3)
    function(1, 2, three=3)


Fixed-position ellipsis (`...`) as `any`
----------------------------------------

`...` can also be used in a fixed position as an ad-hoc `any` matcher.

Assume:

::

    def fetch(location, retry=5, **options): ...

Then:

::

    when(C).fetch("https://example.com/", retry=...)

means `retry` must be present, but its value is ignored.

::

    fetch("https://example.com/", retry=2)
    fetch("https://example.com/", retry=5)

Both are allowed. These raise:

::

    fetch("https://example.com/")
    fetch("https://example.com/", headers={})

So: `...` in a fixed position consumes exactly one value (equivalent to `any`),
and only a trailing positional `...` acts as a rest matcher.

E.g.

::

    when(C).fetch(..., ..., headers=...)
    when(C).fetch(any, any, headers=any)

are equivalent and allow:

::

    fetch("https://foobar.com/", 2, headers={})

.. note::

    ``fetch("https://foobar.com/", 2, headers={})`` and
    ``fetch("https://foobar.com/", retry=2, headers={})`` are *not* the same
    invocations in mockito, even if the function signature would allow both
    variants (i.e. when ``fetch`` is not defined as
    ``def fetch(location, *, retry=5, **options): ...``).

    You are responsible for configuring the style you expect your code to use.
    If your codebase mixes both styles, configure both variants::

        when(C).fetch(..., ..., headers=...)
        when(C).fetch(..., retry=..., headers=...)

We used the built-in Python ``any`` here as marker. That is easy because you
don't have to import anything, just like with ``...``. However, you can also
import the "real" any marker::

    from mockito import any
    from mockito.matchers import any, any_, ANY

We have various spellings for the marker. Choose whatever fits your mood.
This marker also consumes one argument at a time but allows constraints::

    when(C).fetch("https://example.com/", retry=any(int))

With that configuration, naturally follows::

    fetch("https://example.com/", retry=3)    # passes
    fetch("https://example.com/", retry="3")  # raises


Relation to `*args`
-------------------

If you want to match `*args` (multiple arguments), use `args`:

::

    def sum(*args): ...

    when(C).sum(1, 2, *args)

Allows:

::

    sum(1, 2, 3)
    sum(1, 2, 3, 4)

That is similar to plain trailing `...`, but `args` also composes with keyword arguments.

Assume:

::

    def sum(*args, init=0): ...

    when(C).sum(1, 2, *args, init=5)

Allows:

::

    sum(1, 2, 3, init=5)
    sum(1, 2, 3, 4, init=5)

But:

::

    when(C).sum(1, 2, ..., init=5)

uses fixed-position `...` (one value), so it allows:

::

    sum(1, 2, 3, init=5)

and disallows:

::

    sum(1, 2, init=5)
    sum(1, 2, 3, 4, init=5)


Relation to `**kwargs`
----------------------

Ideally we could write:

::

    when(C).fetch("https://example.com/", retry=..., ...)

but that's not valid Python syntax. Use `kwargs` instead:

::

    when(C).fetch("https://example.com/", retry=..., **kwargs)

Allows:

::

    fetch("https://example.com/", retry=2, headers={})

And:

::

    when(C).fetch(..., retry=2, **kwargs)

Allows:

::

    fetch("https://example.com/", retry=2)
    fetch("https://foobar.com/", retry=2)
    fetch("https://foobar.com/", retry=2, headers={})

Use `kwargs` as the rest marker where `...` is not syntactically available
because specific keyword arguments are already configured.
