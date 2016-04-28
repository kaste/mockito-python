Mockito is a spying framework originally based on the Java library with the same name.

.. image:: https://travis-ci.org/kaste/mockito-python.svg?branch=master
    :target: https://travis-ci.org/kaste/mockito-python


Install
=======

``pip install mockito``


Run the tests
-------------

::

    pip install nose
    nosetests


Quick Start
===========

Start with an empty stub::

    from mockito import *

    obj = mock()

    # pass it around, eventually it will be used
    obj.say('Hi')

    # back in the tests, verify interactions
    verify(obj).say('Hi')
    verifyNoMoreInteractions(obj)

Or, say you want to mock the class Dog::

    class Dog(object):
        def bark(self, sound):
            return "%s!" % sound


    # mock the class
    when(Dog).bark('Wuff').thenReturn('Miau!')

    # instantiate
    rex = Dog()
    assert rex.bark('Wuff') == 'Miau!'

    unstub()


Read the docs
=============

http://pythonhosted.org/mockito/


