__STUBBING__=-2

class Mock:
  def __init__(self):
    self.invocations = []
    self.stubbed_invocations = []
    self.mocking_mode = None
  
  def __getattr__(self, method_name):
    if self.mocking_mode == __STUBBING__:
      return InvocationStubber(self, method_name)

    if self.mocking_mode != None:
      return InvocationVerifier(self, method_name)
      
    return InvocationMemorizer(self, method_name)
  
class Invocation:
  def __init__(self, mock, method_name):
    self.method_name = method_name
    self.mock = mock
    self.answers = []
    
  def __cmp__(self, other):
    if self.matches(other):
      return 0
    else:
      return 1
    
  def matches(self, invocation):
    return self.method_name == invocation.method_name and self.params == invocation.params
  
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
        matches+=1
  
    if (matches != self.mock.mocking_mode):
      raise VerificationError()

class InvocationStubber(Invocation):
  def __call__(self, *params, **named_params):
    self.params = params    
    return AnswerSelector(self)

class AnswerSelector():
  def __init__(self, invocation):
    self.invocation = invocation
    
  def thenReturn(self, return_value):
    self.invocation.answers.append(Returns(return_value))     
    #TODO: single method:
    if (self.invocation.mock.stubbed_invocations.count(self.invocation)):
      self.invocation.mock.stubbed_invocations.remove(self.invocation)
      
    self.invocation.mock.stubbed_invocations.append(self.invocation)
    self.invocation.mock.mocking_mode = None
    
  def thenRaise(self, exception):
    self.invocation.answers.append(Throws(exception))     
    #TODO: single method:
    self.invocation.mock.stubbed_invocations.append(self.invocation)
    self.invocation.mock.mocking_mode = None
#    self.invocation.finishStubbing(Throws(exception))

class Returns():
  def __init__(self, return_value):
    self.return_value = return_value
  
  def answer(self):
    return self.return_value

class Throws():
  def __init__(self, exception):
    self.exception = exception
  
  def answer(self):
    raise self.exception
      
class VerificationError(AssertionError):
  pass
  
def verify(mock, count=1):
  mock.mocking_mode = count
  return mock

def times(count):
  return count

def when(mock):
  mock.mocking_mode = __STUBBING__
  return mock