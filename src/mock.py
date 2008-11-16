import mockito

class Mock(object):
  
  def __init__(self):
    self.invocations = []
    self.stubbed_invocations = []
    self.stubbing = None
    self.verification = None
    self.mocked_obj = None
  
  def __getattr__(self, method_name):
    if self.stubbing != None:
      return mockito.StubbedInvocation(self, method_name)
    
    if self.verification != None:
      return mockito.VerifiableInvocation(self, method_name)
      
    return mockito.RememberedInvocation(self, method_name)
  
  def remember(self, invocation):
    self.invocations.insert(0, invocation)
  
  def finishStubbing(self, stubbed_invocation):
    self.stubbed_invocations.insert(0, stubbed_invocation)
    self.stubbing = None
    #TODO needed? self.verification = None
    
  def expectStubbing(self):
    self.stubbing = True