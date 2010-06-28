import matchers
from mock_registry import mock_registry

class InvocationError(AssertionError):
    pass

class Invocation(object):
  def __init__(self, mock, method_name):
    self.method_name = method_name
    self.mock = mock
    self.verified = False
    self.params = ()
    self.named_params = {}
    self.answers = []
    self.strict = mock.strict
    
  def __repr__(self):
    return self.method_name + "(" + ", ".join([repr(p) for p in self.params]) + ")"

  def answer_first(self):
    return self.answers[0].answer()
  
class MatchingInvocation(Invocation):
  @staticmethod
  def compare(p1, p2):
    if isinstance(p1, matchers.Matcher):
      if not p1.matches(p2): return False
    elif p1 != p2: return False
    return True

  def matches(self, invocation):
    if self.method_name != invocation.method_name:
      return False
    if len(self.params) != len(invocation.params):
      return False
    if len(self.named_params) != len(invocation.named_params):
      return False

    for x, p1 in enumerate(self.params):
      if not self.compare(p1, invocation.params[x]):
          return False
      
    for x, p1 in self.named_params.iteritems():
      if not self.compare(p1, invocation.named_params[x]):
          return False
      
    return True
  
class RememberedInvocation(Invocation):
  def __call__(self, *params, **named_params):
    self.params = params
    self.named_params = named_params
    self.mock.remember(self)
    
    for matching_invocation in self.mock.stubbed_invocations:
      if matching_invocation.matches(self):
        return matching_invocation.answer_first()

    return None

class VerifiableInvocation(MatchingInvocation):
  def __call__(self, *params, **named_params):
    self.params = params
    self.named_params = named_params
    matches = 0
    for invocation in self.mock.invocations:
      if self.matches(invocation):
        matches += 1
        invocation.verified = True

    verification = self.mock.pull_verification()
    verification.verify(self, matches)
  
class StubbedInvocation(MatchingInvocation):
  def __init__(self, *params):
    super(StubbedInvocation, self).__init__(*params)  
    if self.mock.strict:
      self.ensure_mocked_object_has_method(self.method_name)
        
  def ensure_mocked_object_has_method(self, method_name):  
    if not self.mock.has_method(method_name):
      raise InvocationError("You tried to stub a method '%s' the object (%s) doesn't have." 
                            % (method_name, self.mock.mocked_obj))
    
        
  def __call__(self, *params, **named_params):
    self.params = params   
    self.named_params = named_params 
    return AnswerSelector(self)
  
  def stub_with(self, answer):
    self.answers.append(answer)
    self.mock.stub(self.method_name)
    self.mock.finish_stubbing(self)
    
class AnswerSelector(object):
  def __init__(self, invocation):
    self.invocation = invocation
    self.answer = None
  
  def thenReturn(self, *return_values):
    for return_value in return_values:
      self.__then(Return(return_value))
    return self
    
  def thenRaise(self, *exceptions):
    for exception in exceptions:
      self.__then(Raise(exception))
    return self

  def __then(self, answer):
    if not self.answer:
      self.answer = CompositeAnswer(answer)
      self.invocation.stub_with(self.answer)
    else:
      self.answer.add(answer)
      
    return self      

class CompositeAnswer(object):
  def __init__(self, answer):
    self.answers = [answer]
    
  def add(self, answer):
    self.answers.insert(0, answer)
    
  def answer(self):
    if len(self.answers) > 1:
      a = self.answers.pop()
    else:
      a = self.answers[0]
      
    return a.answer()

class Raise(object):
  def __init__(self, exception):
    self.exception = exception
    
  def answer(self):
    raise self.exception
  
class Return(object):
  def __init__(self, return_value):
    self.return_value = return_value
    
  def answer(self):
    return self.return_value
