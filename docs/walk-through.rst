The Walk-through
================

The 90% use case is that want to stub out a side effect. This is also known as (monkey-)patching. With mockito, it's::

    from mockito import when

    # stub `os.path.exists`
    when(os.path).exists('/foo').thenReturn(True)

    os.path.exists('/foo')  # => True
    os.path.exists('/bar')  # -> throws unexpected invocation

So in difference to traditional patching, in mockito you always specify concrete arguments (a call signature), and its outcome, usually a return value via `thenReturn` or a raised exception via `thenRaise`. That effectively turns function calls into constants for the time of the test.

There are of course reasons when you don't want to overspecify specific tests. You _just_ want the desired stub answer. Here we go::

    when(os.path).exists(...).thenReturn(True)

    # now, obviously, you get the same answer, regardless of the arguments
    os.path.exists('FooBar')  # => True

You can combine both stubs. E.g. nothing exists, except one file::

    when(os.path).exists(...).thenReturn(False)
    when(os.path).exists('.flake8').thenReturn(True)

And because it's a similar pattern, we can introduce :func:`spy2` here. Spies call through the original implementation of a given function. E.g. everything is as it is, except `'.flake8'` is just not there::

    from mockito import spy2
    spy2(os.path.exists)
    when(os.path).exists('.flake8').thenReturn(False)

When patching, you **MUST** **not** forget to :func:`unstub` of course! You can do this explicitly

::

    from mockito import unstub
    unstub()  # restore os.path module

Usually you do this unconditionally in your `teardown` function. If you're using `pytest`, you could define a fixture instead

::

    # conftest.py
    import pytest

    @pytest.fixture
    def unstub():
        from mockito import unstub
        yield
        unstub()

    # my_test.py
    import pytest
    pytestmark = pytest.mark.usefixtures("unstub")

But very often you just use context managers (aka `with`), and mockito will unstub on 'exit' automatically::

    # E.g. test that `exists` gets never called
    with expect(os.path, times=0).exists('.flake8'):
        # within the block `os.path.exists` is patched
        cached_dir_lookup('.flake8')
    # at the end of the block `os.path` gets unpatched

    # Which is btw roughly the same as doing
    with when(os.path).exists('.flake8'):
        cached_dir_lookup('.flake8')
        verify(os.path, times=0).exists(...)

Now let's mix global module patching with mocks. We want to test the following function using the fab `requests` library::

    import requests

    def get_text(url):
        res = requests.get(url)
        if 200 <= res.status_code < 300:
            return res.text
        return None

How, dare, we did not inject our dependencies! Obviously we can get over that by patching at the module level like before::

    when(requests).get('https://example.com/api').thenReturn(...)

But what should we return? We know it's a `requests.Response` object, (Actually I know this bc I typed this in the ipython REPL first.) But how to construct such a `Response`, its `__init__` doesn't even take any arguments?

Should we actually use a 'real' response object? No, we fake it using :func:`mock`.

::

    # setup
    response = mock({
        'status_code': 200,
        'text': 'Ok'
    }, spec=requests.Response)
    when(requests).get('https://example.com/api').thenReturn(response)

    # run
    assert get_text('https://example.com/api') == 'Ok'

    # done!

Say you want to mock the class Dog::

    class Dog(object):
        def bark(self):
            return 'Wuff'


    # either mock the class
    when(Dog).bark().thenReturn('Miau!')
    # now all instances have a different behavior
    rex = Dog()
    assert rex.bark() == 'Miau!'

    # or mock a concrete instance
    when(rex).bark().thenReturn('Grrrr')
    assert rex.bark() == 'Grrrr'
    # a different dog will still 'Miau!'
    assert Dog().bark() == 'Miau!'

    # be sure to call unstub() once in while
    unstub()


Sure, you can verify your interactions::

    from mockito import verify
    # once again
    rex = Dog()
    when(rex).bark().thenReturn('Grrrr')

    rex.bark()
    rex.bark()

    # `times` defaults to 1
    verify(rex, times=2).bark()


In general mockito is very picky::

    # this will fail because `Dog` has no method named `waggle`
    when(rex).waggle().thenReturn('Nope')
    # this will fail because `bark` does not take any arguments
    when(rex).bark('Grrr').thenReturn('Nope')


    # given this function
    def bark(sound, post='!'):
        return sound + post

    from mockito import kwargs
    when(main).bark('Grrr', **kwargs).thenReturn('Nope')

    # now this one will fail
    bark('Grrr')  # because there are no keyword arguments used
    # this one will fail because `then` does not match the function signature
    bark('Grrr', then='!!')
    # this one will go
    bark('Grrr', post='?')

    # there is also an args matcher
    def add_tasks(*tasks, verbose=False):
        pass

    from mockito import args
    # If you omit the `thenReturn` it will just return `None`
    when(main).add_tasks(*args)

    add_tasks('task1', 'task2')  # will go
    add_tasks()  # will fail
    add_tasks('task1', verbose=True)  # will fail too

    # On Python 3 you can also use `...`
    when(main).add_tasks(...)
    # when(main).add_tasks(Ellipsis) on Python 2

    add_tasks('task1')  # will go
    add_tasks(verbose=True)  # will go
    add_tasks('task1', verbose=True)  # will go
    add_tasks()  # will go


To start with an empty stub use :func:`mock`::

    from mockito import mock

    obj = mock()

    # pass it around, eventually it will be used
    obj.say('Hi')

    # back in the tests, verify the interactions
    verify(obj).say('Hi')

    # by default all invoked methods take any arguments and return None
    # you can configure your expected method calls with the usual `when`
    when(obj).say('Hi').thenReturn('Ho')

    # There is also a shortcut to set some attributes
    obj = mock({
        'hi': 'ho'
    })

    assert obj.hi == 'ho'

    # This would work for methods as well; in this case
    obj = mock({
        'say': lambda _: 'Ho'
    })

    # But you don't have any argument and signature matching
    assert obj.say('Anything') == 'Ho'

    # At least you can verify your calls
    verify(obj).say(...)

    # Btw, you can make screaming strict mocks::
    obj = mock(strict=True)  # every unconfigured, unexpected call will raise


You can use an empty stub specced against a concrete class::

    # Given the above `Dog`
    rex = mock(Dog)

    # Now you can stub out any known method on `Dog` but other will throw
    when(rex).bark().thenReturn('Miau')
    # this one will fail
    when(rex).waggle()

    # These mocks are in general very strict, so even this will fail
    rex.health  # unconfigured attribute

    # Of course you can just set it in a setup routine
    rex.health = 121

    # Or again preconfigure
    rex = mock({'health': 121}, spec=Dog)

    # preconfigure stubbed method
    rex = mock({'bark': lambda sound: 'Miau'}, spec=Dog)

    # as you specced the mock, you get at least function signature matching
    # `bark` does not take any arguments so
    rex.bark('sound')  # will throw TypeError

    # Btw, you can make loose specced mocks::
    rex = mock(Dog, strict=False)


