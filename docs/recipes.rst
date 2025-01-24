.. module:: mockito


Recipes
=======


Classes as factories
--------------------

We want to test the following code::

    import requests

    def fetch(url):
        session = requests.Session()
        return session.get(url)

In a traditional sense this code is not designed for *testability*. But we don't care here.

Python has no `new` keyword to get fresh instances from classes. Man, that was a good decision, Guido! So the uppercase `S` in `requests.Session()` doesn't have to stop us in any way. It looks like a function call, and we treat it like such: The plan is to replace `Session` with a factory function that returns a (mocked) session::

    from mockito import when, mock, verifyStubbedInvocationsAreUsed

    def test_fetch(unstub):
        url = 'http://example.com/'
        response = mock({'text': 'Ok'}, spec=requests.Response)
        # remember: `mock` here just creates an empty object specced after
        #           requests.Session
        session = mock(requests.Session)
        # `when` here configures the mock
        when(session).get(url).thenReturn(response)
        # `when` *patches* the globally available *requests* module
        when(requests).Session().thenReturn(session)  # <=

        res = fetch(url)
        assert res.text == 'Ok'

        # no need to verify anything here, if we get the expected response
        # back, `url` must have been passed through the system, otherwise
        # mockito would have thrown.
        # We *could* ensure that our mocks are actually used, if we want:
        verifyStubbedInvocationsAreUsed()


Faking magic methods
--------------------

We want to test the following code::

    import requests

    def fetch_2(url):
        with requests.Session() as session:
            return session.get(url)

It's basically the same problem, but we need to add support for the context manager, the `with` interface::

    from mockito import when, mock, args

    def test_fetch_with(unstub):
        url = 'http://example.com/'
        response = mock({'text': 'Ok'}, spec=requests.Response)

        session = mock(requests.Session)
        when(session).get(url).thenReturn(response)
        when(session).__enter__().thenReturn(session)  # <=
        when(session).__exit__(*args)                  # <=

        when(requests).Session().thenReturn(session)

        res = fetch_2(url)
        assert res.text == 'Ok'


Deepcopies
----------

Python's `deepcopy` is tied to `__deepcopy__`, in a nutshell `deepcopy(m)` will call `m.__deepcopy__()`.
For a strict mock, `deepcopy(m)` will raise an error as long as the call is unexpected -- as usual.

While you could completely fake it --

::

    when(m).__deepcopy__(...).thenReturn(42)

-- you could also enable the standard implementation by configuring the mock, e.g.

::

    mock({"__deepcopy__": None}, strict=True)

Dumb mocks are copied correctly by default.

However, there is a possible catch: deep mutable objects must be set on the mock's instance, not the class.
And the constructors configuration is set on the class, not the instance.  Huh?  Let's show an example::

    m = mock()
    m.foo = [1]  # <= this is set on the instance, not the class

    m = mock({"foo": [1]})  # <= this is set on the class, not the instance

Don't rely on that latter "feature", initially the configurataion was meant to only set methods, and especially
special, dunder methods, -- and properties.  If we get proper support for properties, we'll likely make a change
here too.

Btw, `copy` will *just work* for strict mocks and does not raise an error when not configured/expected.  This is
just not implemented and considered not-worth-the-effort.
