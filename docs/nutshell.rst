TL;DR
-----


::

    >>> from mockito import *
    >>> myMock = mock()
    >>> when(myMock).getStuff().thenReturn('stuff')
    <mockito.invocation.AnswerSelector object at 0x00CA0BB0>
    >>> myMock.getStuff()
    'stuff'
    >>> verify(myMock).getStuff()

    >>> when(myMock).doSomething().thenRaise(Exception('Did a bad thing'))
    <mockito.invocation.AnswerSelector object at 0x00CA0C10>
    >>> myMock.doSomething()
    Traceback (most recent call last):
    <...>
    Exception: Did a bad thing

No difference whatsoever when you mock modules

::

    >>> import os.path
    >>> when(os.path).exists('somewhere/somewhat').thenReturn(True)
    <mockito.invocation.AnswerSelector object at 0x00D394F0>
    >>> when(os.path).exists('somewhere/something').thenReturn(False)
    <mockito.invocation.AnswerSelector object at 0x00C7D1B0>
    >>> os.path.exists('somewhere/somewhat')
    True
    >>> os.path.exists('somewhere/something')
    False
    >>> os.path.exists('another_place')
    Traceback (most recent call last):
    <...>
    mockito.invocation.InvocationError: You called exists with ('another_place',) as
     arguments but we did not expect that.

    >>> when(os.path).exist('./somewhat').thenReturn(True)
    Traceback (most recent call last):
    <...>
    mockito.invocation.InvocationError: You tried to stub a method 'exist' the objec
    t (<module 'ntpath' from ...>) doesn't have.

If that's too strict, you can change it

::

    >>> when(os.path, strict=False).exist('another_place').thenReturn('well, nice he
    re')
    <mockito.invocation.AnswerSelector object at 0x00D429B0>
    >>> os.path.exist('another_place')
    'well, nice here'
    >>> os.path.exist('and here?')
    >>>

No surprise, you can do the same with your classes

::

    >>> class Dog(object):
    ...   def bark(self):
    ...     return "Wau"
    ...
    >>> when(Dog).bark().thenReturn('Miau!')
    <mockito.invocation.AnswerSelector object at 0x00D42390>
    >>> rex = Dog()
    >>> rex.bark()
    'Miau!'

or just with instances, first unstub

::

    >>> unstub()
    >>> rex.bark()
    'Wau'

then do

::

    >>> when(rex).bark().thenReturn('Grrrrr').thenReturn('Wuff')
    <mockito.invocation.AnswerSelector object at 0x00D48790>

and get something different on consecutive calls

::

    >>> rex.bark()
    'Grrrrr'
    >>> rex.bark()
    'Wuff'
    >>> rex.bark()
    'Wuff'

and since you stubbed an instance, a different instance will not be stubbed

::

    >>> bello = Dog()
    >>> bello.bark()
    'Wau'

You have 4 modifiers when verifying

::

    >>> verify(rex, times=3).bark()
    >>> verify(rex, atleast=1).bark()
    >>> verify(rex, atmost=3).bark()
    >>> verify(rex, between=[1,3]).bark()
    >>>

Finally, we have two matchers

::

    >>> myMock = mock()
    >>> when(myMock).do(any(int)).thenReturn('A number')
    <mockito.invocation.AnswerSelector object at 0x00D394B0>
    >>> when(myMock).do(any(str)).thenReturn('A string')
    <mockito.invocation.AnswerSelector object at 0x00D39E70>
    >>> myMock.do(2)
    'A number'
    >>> myMock.do('times')
    'A string'

    >>> verify(myMock).do(any(int))
    >>> verify(myMock).do(any(str))
    >>> verify(myMock).do(contains('time'))

   >>> exit()

.. toctree::
   :maxdepth: 2

