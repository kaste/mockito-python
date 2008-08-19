import inspect

class StaticMocker():
  """Deals with static AND class methods AND with modules functions"""
  
  def __init__(self):
    self.originals = []
    self.static_mocks = {}

  def stub(self, invocation):
    self.static_mocks[invocation.getMockedObj()] = invocation.mock
    original_method = invocation.getMockedObj().__dict__.get(invocation.method_name)
    original = (invocation.getMockedObj(), invocation.method_name, original_method)

    def new_static_method(*params, **named_params): 
      if isinstance(original_method, classmethod): params = params[1:]
      i = invocation.mock.__getattr__(invocation.method_name)
      return i.__call__(*params, **named_params)
      
    self.originals.append(original)
    if isinstance(original_method, staticmethod):
      setattr(invocation.getMockedObj(), invocation.method_name, staticmethod(new_static_method))
    elif isinstance(original_method, classmethod): 
      setattr(invocation.getMockedObj(), invocation.method_name, classmethod(new_static_method))
    elif inspect.ismodule(invocation.getMockedObj()):
      setattr(invocation.getMockedObj(), invocation.method_name, new_static_method)      
    else:
      # TODO create decent error. is it necessary? this case is only useful for library debugging        
      raise "Only modules functions, static and class methods can be stubbed"    
    
  def getMockFor(self, cls):
    return self.static_mocks[cls]
  
  def unstub(self):
    while self.originals:
      cls, original_method_name, original_method = self.originals.pop()
      setattr(cls, original_method_name, original_method)
