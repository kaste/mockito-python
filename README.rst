Mockito is a spying framework originally based on the Java library with the same name.

.. image:: https://travis-ci.org/kaste/mockito-python.svg?branch=master
    :target: https://travis-ci.org/kaste/mockito-python


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



Run the tests
-------------

::

    pip install nose
    nosetests


