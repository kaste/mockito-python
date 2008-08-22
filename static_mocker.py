import inspect
import types

class StaticMocker():
  """Deals with static methods AND class methods AND with module methods. 
  To me they all are just static, procedural-like functions, hence StaticMocker"""
  
  def __init__(self):
    self.originals = []
    self.static_mocks = {}

  def stub(self, invocation):
    self.static_mocks[invocation.getMockedObj()] = invocation.mock
    # TODO LoD    
    original_method = invocation.getMockedObj().__dict__.get(invocation.method_name)
    # TODO original should hold entire invocation?    
    original = (invocation.getMockedObj(), invocation.method_name, original_method)

    def mocked_method(*params, **named_params): 
      if isinstance(original_method, classmethod): params = params[1:]
      i = invocation.mock.__getattr__(invocation.method_name)
      return i.__call__(*params, **named_params)
      
    self.originals.append(original)
    # TODO questions should be asked on invocation object?    
    if isinstance(original_method, staticmethod):
      setattr(invocation.getMockedObj(), invocation.method_name, staticmethod(mocked_method))
    elif isinstance(original_method, classmethod): 
      setattr(invocation.getMockedObj(), invocation.method_name, classmethod(mocked_method))
    elif inspect.ismodule(invocation.getMockedObj()):
      setattr(invocation.getMockedObj(), invocation.method_name, mocked_method)      
    else:
      # TODO create decent error. is it necessary? this case is only useful for library debugging        
      raise "Only modules functions, static and class methods can be stubbed"    
    
  def getMockFor(self, cls):
    return self.static_mocks[cls]
  
  def accepts(self, obj):
     return inspect.ismodule(obj) or isinstance(obj, types.ClassType)
  
  def unstub(self):
    while self.originals:
      cls, original_method_name, original_method = self.originals.pop()
      setattr(cls, original_method_name, original_method)
