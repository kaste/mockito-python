Mockito is a spying framework originally based on the Java library with the same name.


Install
=======

``pip install mockito``


Walk-through
============

Say you want to mock the class Dog::

    class Dog(object):
        def bark(self, sound):
            return "%s!" % sound

To get you started::

    from mockito import *

    # mock the class
    when(Dog).bark('Wuff').thenReturn('Miau!')

    # instantiate
    rex = Dog()
    assert rex.bark('Wuff') == 'Miau!'

    unstub()

You can also start with an empty stub::

    obj = mock()

    # pass it around, eventually it will be used
    obj.say('Hi')

    # verify interactions
    verify(obj).say('Hi')
    verifyNoMoreInteractions(obj)



Currently you can find some more docs at http://code.google.com/p/mockito-python/

Feel free to contribute more documentation or feedback!


To run all tests::

    pip install nose
    nosetests



.. image:: https://travis-ci.org/kaste/mockito-python.svg?branch=master
    :target: https://travis-ci.org/kaste/mockito-python