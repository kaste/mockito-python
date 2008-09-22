import matchers
from static_mocker import *
from method_printer import *

_STUBBING_ = -2

_STATIC_MOCKER_ = StaticMocker()

_RETURNS_ = 1
_THROWS_ = 2

class Mock:
  
  def __init__(self):
    self.invocations = []
    self.stubbed_invocations = []
    self.mocking_mode = None
    self.mocked_obj = None
  
  def __getattr__(self, method_name):
    if self.isStubbing() or self.isStubbingStatic():
      return InvocationStubber(self, method_name)
    
    if self.mocking_mode >= 0:
      return InvocationVerifier(self, method_name)
      
    return InvocationMemorizer(self, method_name)
  
  def isStubbingStatic(self):
    return self.isStubbing() and _STATIC_MOCKER_.accepts(self.mocked_obj) 
  
  def isStubbing(self):
    return self.mocking_mode == _STUBBING_
  
  def finishStubbing(self, invocation):
    if (self.stubbed_invocations.count(invocation)):
      self.stubbed_invocations.remove(invocation)
      
    self.stubbed_invocations.append(invocation)
    
    if (self.isStubbingStatic()):
      _STATIC_MOCKER_.stub(invocation)
      
    self.mocking_mode = None
    
class Invocation:
  def __init__(self, mock, method_name):
    self.method_name = method_name
    self.mock = mock
    self.answers = []
    self.verified = False
  
  def getMockedObj(self):
    return self.mock.mocked_obj
  
  def getRealMethod(self):
    return self.getMockedObj().__dict__.get(self.method_name)
  
  def replaceMethod(self, new_method):
    setattr(self.getMockedObj(), self.method_name, new_method)
    
  def __cmp__(self, other):
    return 0 if self.matches(other) else 1
    
  def matches(self, invocation):
    if self.method_name == invocation.method_name and self.params == invocation.params:
      return True
    if len(self.params) != len(invocation.params):
      return False
    return self.__compareUsingMatchers(invocation)

  def __compareUsingMatchers(self, invocation):  
    for x, p1 in enumerate(self.params):
      p2 = invocation.params[x]
      if isinstance(p1, matchers.Matcher):
        if not p1.matches(p2): return False
      elif p1 != p2: return False
    return True
  
  def stubWith(self, answer, chained_mode):
    if chained_mode:
        self.answers[-1].append(answer.current())
    else:
        self.answers.append(answer)
        
    self.mock.finishStubbing(self)
    
class InvocationMemorizer(Invocation):
  def __call__(self, *params, **named_params):
    self.params = params
    self.mock.invocations.append(self)
    
    for invocation in self.mock.stubbed_invocations:
      if self.matches(invocation):
        return invocation.answers[0].answer()
    
    return None
  
  def __str__(self):
    return self.method_name + str(self.params)
  
class InvocationVerifier(Invocation):
  def __call__(self, *params, **named_params):
    self.params = params
    matches = 0
    for invocation in self.mock.invocations:
      if self.matches(invocation):
        matches += 1
        invocation.verified = True
  
    if (self.mock.mocking_mode == 1 and matches != self.mock.mocking_mode):
      m = MethodPrinter().printIt(self.method_name, *self.params)
      raise VerificationError("\nWanted but not invoked: " + m)
    elif (matches != self.mock.mocking_mode):
      raise VerificationError("Wanted times: " + str(self.mock.mocking_mode) + ", actual times: " + str(matches))
  
class InvocationStubber(Invocation):
  def __call__(self, *params, **named_params):
    self.params = params    
    return AnswerSelector(self)
  
class AnswerSelector():
  def __init__(self, invocation):
    self.invocation = invocation
    self.chained_mode = False
    
  def thenReturn(self, return_value):
    return self.__then(Answer(return_value, _RETURNS_))
    
  def thenRaise(self, exception):
    return self.__then(Answer(exception, _THROWS_))

  def __then(self, answer):
    self.invocation.stubWith(answer, self.chained_mode)     
    self.chained_mode = True
    return self      

class Answer():
  def __init__(self, value, type):
    self.answers = [[value, type]]
    self.index = 0

  def current(self):
    return self.answers[self.index]

  def append(self, answer):
    self.answers.append(answer)

  def answer(self):
    answer = self.current()[0] 
    type = self.current()[1]
    if self.index < len(self.answers) - 1: self.index += 1
    if type == _THROWS_: raise answer
    return answer

class VerificationError(AssertionError):
  pass

class ArgumentError(Exception):
  pass
  
def verify(obj, times=1):
  if times < 0:
    raise ArgumentError("'times' argument has invalid value. It should be at least 0. You wanted to set it to: " + str(times))

  mock = _STATIC_MOCKER_.getMockFor(obj) if _STATIC_MOCKER_.accepts(obj) else obj
  mock.mocking_mode = times
  return mock

def times(count):
  return count

def when(obj):
  #TODO verify obj is a class or a mock
  
  mock = obj
  if (_STATIC_MOCKER_.accepts(obj)):
    mock = Mock()
    mock.mocked_obj = obj

  mock.mocking_mode = _STUBBING_
  return mock

def unstub():
  """Unstubs all stubbed static methods and class methods"""
  
  _STATIC_MOCKER_.unstub()

def verifyNoMoreInteractions(*mocks):
  for mock in mocks:
    for i in mock.invocations:
      if not i.verified:
        raise VerificationError("\nUnwanted interaction: " + str(i))
      
def any(wanted_type=None):
  """Matches any() argument OR any(SomeClass) argument
     Examples:
       when(mock).foo(any()).thenReturn(1)
       verify(mock).foo(any(int))
  """

  return matchers.Any(wanted_type)     
        
def contains(sub):
  return matchers.Contains(sub)