.. mockito-python documentation master file, created by
   sphinx-quickstart on Tue Apr 26 14:00:19 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


Mockito is a spying framework originally based on the Java library with the same name.

.. image:: https://travis-ci.org/kaste/mockito-python.svg?branch=master
    :target: https://travis-ci.org/kaste/mockito-python


Install
=======

``pip install mockito``


If you want, run the tests
-------------

::

    pip install nose
    nosetests



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



There is a another :doc:`TL;DR <nutshell>` and *some* more docs at http://code.google.com/p/mockito-python/

**Report issues, contribute more documentation or give feedback at `Github <https://github.com/kaste/mockito-python>`_!**


.. Contents:

.. .. toctree::
..    :maxdepth: 2

..    nutshell



.. Indices and tables
.. ==================

.. * :ref:`genindex`
.. * :ref:`modindex`
.. * :ref:`search`

