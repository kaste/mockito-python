import matchers
from static_mocker import *

_STUBBING_ = -2
_AT_LEAST_ = -3
_AT_MOST_ = -4
_BETWEEN_ = -5

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
    
    if self.mocking_mode >= 0 or self.mocking_mode == _AT_LEAST_ or self.mocking_mode == _AT_MOST_ or self.mocking_mode == _BETWEEN_:
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
    self.params = ()
  
  def getMockedObj(self):
    return self.mock.mocked_obj
  
  def getRealMethod(self):
    return self.getMockedObj().__dict__.get(self.method_name)
  
  def replaceMethod(self, new_method):
    setattr(self.getMockedObj(), self.method_name, new_method)
    
  def __cmp__(self, other):
    if self.matches(other): return 0
    else: return 1
    
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
    
  def __str__(self):
    return self.method_name + str(self.params)    
    
class InvocationMemorizer(Invocation):
  def __call__(self, *params, **named_params):
    self.params = params
    self.mock.invocations.append(self)
    
    for invocation in self.mock.stubbed_invocations:
      if self.matches(invocation):
        return invocation.answers[0].answer()
    
    return None
  
class InvocationVerifier(Invocation):
  def __call__(self, *params, **named_params):
    self.params = params
    matches = 0
    for invocation in self.mock.invocations:
      if self.matches(invocation):
        matches += 1
        invocation.verified = True

    # TODO: to be refactored soon. maybe separate class for each verification modes?   
    if self.mock.mocking_mode == 1 and matches != self.mock.mocking_mode:
      raise VerificationError("\nWanted but not invoked: " + str(self))
    elif self.mock.mocking_mode > 1 and matches != self.mock.mocking_mode:
      raise VerificationError("Wanted times: " + str(self.mock.mocking_mode) + ", actual times: " + str(matches))
    elif self.mock.mocking_mode == _AT_LEAST_ and matches < self.mock.mocking_mode_value: 
      raise VerificationError("Wanted at least: " + str(self.mock.mocking_mode_value) + ", actual times: " + str(matches))
    elif self.mock.mocking_mode == _AT_MOST_ and matches > self.mock.mocking_mode_value: 
      raise VerificationError("Wanted at most: " + str(self.mock.mocking_mode_value) + ", actual times: " + str(matches))
    elif self.mock.mocking_mode == _BETWEEN_ and (matches < self.mock.mocking_mode_value[0] or matches > self.mock.mocking_mode_value[1]): 
      raise VerificationError("Wanted between: " + str(self.mock.mocking_mode_value) + ", actual times: " + str(matches))
  
class InvocationStubber(Invocation):
  def __call__(self, *params, **named_params):
    self.params = params    
    return AnswerSelector(self)
  
class AnswerSelector:
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

class Answer:
  def __init__(self, value, type):
    self.answers = [[value, type]]
    self.index = 0

  def current(self):
    return self.answers[self.index]

  def append(self, answer):
    self.answers.append(answer)

  def answer(self):
    answer, type = self.current() 
    if self.index < len(self.answers) - 1: self.index += 1
    if type == _THROWS_: raise answer
    return answer

class VerificationError(AssertionError):
  pass

class ArgumentError(Exception):
  pass

def verify(obj, times=1, atLeast=None, atMost=None, between=None):
# TODO: refactor this mess below...  
  if times < 0:
    raise ArgumentError("'times' argument has invalid value. It should be at least 0. You wanted to set it to: " + str(times))
  if len(filter(lambda x: x, [atLeast, atMost, between])) > 1:
    raise ArgumentError("Sure you know what you are doing? You can set only one of the arguments: 'atLeast', 'atMost' or 'between'.")
  if (atLeast and atLeast < 1) or atLeast == 0:
    raise ArgumentError("'atLeast' argument has invalid value. It should be at least 1.  You wanted to set it to: " + str(atLeast))
  if (atMost and atMost < 1) or atMost == 0:
    raise ArgumentError("'atMost' argument has invalid value. It should be at least 1.  You wanted to set it to: " + str(atMost))
  if between:
    start, end = between
    if start > end or start < 0:
      raise ArgumentError("'between' argument has invalid value. It should be both positive values with second number not greater than first e.g. [1, 4] or [0, 3] or [2, 2].  You wanted to set it to: " + str(between))
   
  if _STATIC_MOCKER_.accepts(obj): mock = _STATIC_MOCKER_.getMockFor(obj)  
  else: mock = obj
  
  mock.mocking_mode = times
  if atLeast:
      mock.mocking_mode = _AT_LEAST_
      mock.mocking_mode_value = atLeast
  elif atMost:
      mock.mocking_mode = _AT_MOST_
      mock.mocking_mode_value = atMost      
  elif between:
      mock.mocking_mode = _BETWEEN_
      mock.mocking_mode_value = between      
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
      
def verifyZeroInteractions(*mocks):
  verifyNoMoreInteractions(*mocks)
      
def any(wanted_type=None):
  """Matches any() argument OR any(SomeClass) argument
     Examples:
       when(mock).foo(any()).thenReturn(1)
       verify(mock).foo(any(int))
  """

  return matchers.Any(wanted_type)     
        
def contains(sub):
  return matchers.Contains(sub)