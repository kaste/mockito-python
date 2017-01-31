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

    from mockito import when, mock

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


