class StaticMocker():
  """Deals with both static AND class methods"""
  
  def __init__(self):
    self.originals = []
    self.static_mocks = {}
    
  def stub(self, invocation):
    self.static_mocks[invocation.getMockedObj()] = invocation.mock
    def new_static_method(*params, **named_params): 
      i = invocation.mock.__getattr__(invocation.method_name)
      return i.__call__(*params, **named_params)
      
    original_method = getattr(invocation.getMockedObj(), invocation.method_name)
    original = (invocation.getMockedObj(), original_method)
    self.originals.append(original)
    setattr(invocation.getMockedObj(), invocation.method_name, staticmethod(new_static_method))
    
  def getMockFor(self, cls):
    return self.static_mocks[cls]
  
  def unstub(self):
    while self.originals:
      cls, original_method = self.originals.pop();
      setattr(cls, original_method.__name__, staticmethod(original_method))   