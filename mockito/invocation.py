import matchers
import static_mocker

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

    verification = self.mock.pull_verification()
    verification.verify(self, matches)
  
class StubbedInvocation(MatchingInvocation):
  def __call__(self, *params, **named_params):
    self.params = params    
    return AnswerSelector(self)
  
  def stub_with(self, answer):
    self.answers.append(answer)
    static_mocker.INSTANCE.stub(self)
    self.mock.finish_stubbing(self)
    
  def get_original_method(self):
    return self.mock.mocked_obj.__dict__.get(self.method_name)
  
  def replace_method(self, new_method):
    setattr(self.mock.mocked_obj, self.method_name, new_method)  
    
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
    if (not self.answer):
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