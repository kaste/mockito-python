import matchers
from static_mocker import *
from mock import *

_STATIC_MOCKER_ = StaticMocker()

_RETURNS_ = 1
_THROWS_ = 2

class Invocation(object):
  def __init__(self, mock, method_name):
    self.method_name = method_name
    self.mock = mock
    self.verified = False
    self.params = ()
    self.answers = []
    
  def __repr__(self):
    return self.method_name + str(self.params)   
  
class MatchingInvocation(Invocation):
   
  def matches(self, invocation):
    if self.method_name != invocation.method_name:
      return False
    if len(self.params) != len(invocation.params):
      return False
    
    for x, p1 in enumerate(self.params):
      p2 = invocation.params[x]
      if isinstance(p1, matchers.Matcher):
        if not p1.matches(p2): return False
      elif p1 != p2: return False
    
    return True
  
class RememberedInvocation(Invocation):
  def __call__(self, *params, **named_params):
    self.params = params
    self.mock.remember(self)
    
    for matching_invocation in self.mock.stubbed_invocations:
      if matching_invocation.matches(self):
        #TODO LoD    
        return matching_invocation.answers[0].answer()
    
    return None

class VerifiableInvocation(MatchingInvocation):
  def __call__(self, *params, **named_params):
    self.params = params
    matches = 0
    for invocation in self.mock.invocations:
      if self.matches(invocation):
        matches += 1
        invocation.verified = True

    verification = self.mock.verification
    self.mock.verification = None
    verification.verify(self, matches)
  
class StubbedInvocation(MatchingInvocation):
  def __call__(self, *params, **named_params):
    self.params = params    
    return AnswerSelector(self)
  
  def stubWith(self, answer, chained_mode):
    if chained_mode:
        self.answers[-1].append(answer.current())
    else:
        self.answers.append(answer)
        
    self.mock.finishStubbing(self)
    _STATIC_MOCKER_.stub(self)
    
  def getOriginalMethod(self):
    return self.mock.mocked_obj.__dict__.get(self.method_name)
  
  def replaceMethod(self, new_method):
    setattr(self.mock.mocked_obj, self.method_name, new_method)    
    
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
  
  if atLeast:
    mock.verification = AtLeast(atLeast)
  elif atMost:
    mock.verification = AtMost(atMost)
  elif between:
    mock.verification = Between(*between)
  else:
    mock.verification = Times(times)
  return mock

class AtLeast(object):
  def __init__(self, wanted_count):
    self.wanted_count = wanted_count
    
  def verify(self, invocation, actual_count):
    if actual_count < self.wanted_count: 
      raise VerificationError("Wanted at least: " + str(self.wanted_count) + ", actual times: " + str(actual_count))
    
class AtMost(object):
  def __init__(self, wanted_count):
    self.wanted_count = wanted_count
    
  def verify(self, invocation, actual_count):
    if actual_count > self.wanted_count: 
      raise VerificationError("Wanted at most: " + str(self.wanted_count) + ", actual times: " + str(actual_count))

class Between(object):
  def __init__(self, wanted_from, wanted_to):
    self.wanted_from = wanted_from
    self.wanted_to = wanted_to
    
  def verify(self, invocation, actual_count):
    if actual_count < self.wanted_from or actual_count > self.wanted_to: 
      raise VerificationError("Wanted between: " + str((self.wanted_from, self.wanted_to)) + ", actual times: " + str(actual_count))
    
class Times(object):
  def __init__(self, wanted_count):
    self.wanted_count = wanted_count
    
  def verify(self, invocation, actual_count):
    if actual_count != self.wanted_count:
      raise VerificationError("\nWanted but not invoked: " + str(invocation))
    elif actual_count != self.wanted_count:
      raise VerificationError("Wanted times: " + str(self.wanted_count) + ", actual times: " + str(actual_count))

def times(count):
  return count

def when(obj):
  #TODO verify obj is a class or a mock
  
  mock = obj
  if (_STATIC_MOCKER_.accepts(obj)):
    mock = Mock()
    mock.mocked_obj = obj

  mock.expectStubbing()
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