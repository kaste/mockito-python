class Mock:
  def __init__(self):
    self.invocations = []
    self.verification_mode = None
  
  def __getattr__(self, method_name):
    if self.verification_mode:
      return InvocationVerifier(self, method_name)
      
    return InvocationMemorizer(self, method_name)
  
class Invocation:
  def __init__(self, mock, method_name):
    self.method_name = method_name
    self.mock = mock

  def matches(self, invocation):
    return self.method_name == invocation.method_name and self.params == invocation.params
  
class InvocationMemorizer(Invocation):
  def __call__(self, *params, **named_params):
    self.params = params
    self.mock.invocations.append(self)
    return 1
  
class InvocationVerifier(Invocation):
  def __call__(self, *params, **named_params):
    self.params = params
    matches = 0
    for invocation in self.mock.invocations:
      if self.matches(invocation):
        matches+=1
  
    if (matches != self.mock.verification_mode.count):
      raise VerificationError()
  
class VerificationMode:
  def __init__(self, count):
    self.count = count
    
class VerificationError(AssertionError):
  pass 
  
def verify(mock, count=1):
  mock.verification_mode = VerificationMode(count)
  return mock

def times(count):
  return count