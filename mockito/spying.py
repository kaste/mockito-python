# Copyright (c) 2008-2016 Szczepan Faber, Serhiy Oplakanets, Herr Kaste
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

'''Spying on real objects.'''

import inspect

from .invocation import RememberedProxyInvocation
from .mocking import Mock, _Dummy, mock_registry

__all__ = ['spy']


def spy(object):
    """Spy an object

    Spying means that all functions will behave as before, so they will
    be side effects, but the interactions can be verified afterwards.

    Returns Dummy-like, almost empty object as proxy to ``object``.

    The *returned* object must be injected and used by the code under test;
    after that all interactions can be verified as usual.
    T.i. the original object **will not be patched**, and has no further
    knowledge as before.

    E.g.::

        import time
        time = spy(time)
        # inject time
        do_work(..., time)
        verify(time).time()

    """
    if inspect.isclass(object) or inspect.ismodule(object):
        class_ = None
    else:
        class_ = object.__class__

    class Spy(_Dummy):
        if class_:
            __class__ = class_

        def __getattr__(self, method_name):
            return RememberedProxyInvocation(theMock, method_name)

        def __repr__(self):
            name = 'Spied'
            if class_:
                name += class_.__name__
            return "<%s id=%s>" % (name, id(self))


    obj = Spy()
    theMock = Mock(obj, strict=True, spec=object)

    mock_registry.register(obj, theMock)
    return obj

