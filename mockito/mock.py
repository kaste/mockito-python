import invocation

class Dummy(object): pass

class Mock(object):
  
  def __init__(self, mocked_obj=None, strict=True):
    self.invocations = []
    self.stubbed_invocations = []
    self.stubbing = None
    self.verification = None
    if mocked_obj is None:
        mocked_obj = Dummy()
        strict = False
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

  def has_method(self, method_name):
    return hasattr(self.mocked_obj, method_name)
    
  def get_method(self, method_name):
    return self.mocked_obj.__dict__.get(method_name)

  def replace_method(self, method_name, new_method):
    setattr(self.mocked_obj, method_name, new_method)  

