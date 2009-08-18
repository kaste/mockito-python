import invocation

class Mock(object):
  
  def __init__(self, mocked_obj=None, strict=True):
    self.invocations = []
    self.stubbed_invocations = []
    self.stubbing = None
    self.verification = None
    self.mocked_obj = mocked_obj
    self.strict = strict
  
  def __getattr__(self, method_name):
    if self.stubbing is not None:
      return invocation.StubbedInvocation(self, method_name)
    
    if self.verification is not None:
      return invocation.VerifiableInvocation(self, method_name)
      
    return invocation.RememberedInvocation(self, method_name)
  
  def remember(self, invocation):
    self.invocations.insert(0, invocation)
  
  def finish_stubbing(self, stubbed_invocation):
    self.stubbed_invocations.insert(0, stubbed_invocation)
    self.stubbing = None
    
  def expect_stubbing(self):
    self.stubbing = True
    
  def pull_verification(self):
    v = self.verification
    self.verification = None
    return v