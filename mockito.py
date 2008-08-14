import types
from static_mocker import *

_STUBBING_ = -2
_STUBBING_STATICS_ = -3

_STATIC_MOCKER_ = StaticMocker()

_RETURNS_ = 1
_THROWS_ = 2

class Mock:
  
  def __init__(self):
    self.invocations = []
    self.stubbed_invocations = []
    self.mocking_mode = None
    self.mocked = None
  
  def __getattr__(self, method_name):
    if self.mocking_mode == _STUBBING_ or self.mocking_mode == _STUBBING_STATICS_:
      return InvocationStubber(self, method_name)
    
    if self.mocking_mode >= 0:
      return InvocationVerifier(self, method_name)
      
    return InvocationMemorizer(self, method_name)
  
  def finishStubbing(self, invocation):
    if (self.stubbed_invocations.count(invocation)):
      self.stubbed_invocations.remove(invocation)
      
    self.stubbed_invocations.append(invocation)
    
    if (self.mocking_mode == _STUBBING_STATICS_):
      _STATIC_MOCKER_.stub(invocation)
      
    self.mocking_mode = None
    
class Invocation:
  def __init__(self, mock, method_name):
    self.method_name = method_name
    self.mock = mock
    self.answers = []
    self.verified = False
  
  def getMocked(self):
    return self.mock.mocked
    
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
        if isinstance(p1, Matcher):
            if not p1.satisfies(p2): return False
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
  
class InvocationVerifier(Invocation):
  def __call__(self, *params, **named_params):
    self.params = params
    matches = 0
    for invocation in self.mock.invocations:
      if self.matches(invocation):
        matches += 1
        invocation.verified = True
  
    if (matches != self.mock.mocking_mode):
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
      
  if (isinstance(obj, types.ClassType)):
    mock = _STATIC_MOCKER_.static_mocks[obj]
  else:
    mock = obj
  
  mock.mocking_mode = times
  return mock

def times(count):
  return count

def when(obj):
  #TODO verify obj is a class or a mock
  if (isinstance(obj, types.ClassType)):
    mock = Mock()
    mock.mocking_mode = _STUBBING_STATICS_
    mock.mocked = obj
    return mock
  
  obj.mocking_mode = _STUBBING_  
  return obj

def unstub():
  """Unstubs all stubbed static methods / class methods"""
  while _STATIC_MOCKER_.stubbed_statics:
    cls, original_method = _STATIC_MOCKER_.stubbed_statics.pop();
    setattr(cls, original_method.__name__, staticmethod(original_method))    

def verifyNoMoreInteractions(*mocks):
  for mock in mocks:
    for i in mock.invocations:
      if not i.verified:
        raise VerificationError("Unwanted interaction: " + i.method_name)
      
class Matcher:
  def satisfies(self, arg):
      pass
  
class any(Matcher):           
  def __init__(self, type=None):
      self.type = type
    
  def satisfies(self, arg):
      return isinstance(arg, self.type) if self.type else True

class contains(Matcher):
  def __init__(self, sub):
      self.sub = sub
      
  def satisfies(self, arg):
      return self.sub and len(self.sub) > 0 and arg.find(self.sub) > -1