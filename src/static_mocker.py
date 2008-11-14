import inspect
import types

class StaticMocker:
  """Deals with static methods AND class methods AND with module functions. 
  As they all are just static, procedural-like functions, hence StaticMocker"""
  
  def __init__(self):
    self.originals = []
    self.static_mocks = {}

  def stub(self, invocation):
    self.static_mocks[invocation.getMockedObj()] = invocation.mock
    original_method = invocation.getRealMethod()
    original = (original_method, invocation)
    self.originals.append(original)

    self._replaceMethod(invocation, original_method)
    
  def _replaceMethod(self, invocation, original_method):
    
    def new_mocked_method(*params, **named_params): 
      if self._is_classmethod(original_method): params = params[1:]
      call = invocation.mock.__getattr__(invocation.method_name)
      return call(*params, **named_params)
      
    if self._is_staticmethod(original_method):
      invocation.replaceMethod(staticmethod(new_mocked_method))
    elif self._is_classmethod(original_method): 
      invocation.replaceMethod(classmethod(new_mocked_method))
    elif inspect.ismodule(invocation.getMockedObj()):
      invocation.replaceMethod(new_mocked_method)
    else:
      # TODO create decent error. is it necessary? this case is only useful for library debugging        
      raise "Only module functions, static and class methods can be stubbed"  
    
  def _is_classmethod(self, method):
    return isinstance(method, classmethod)
  
  def _is_staticmethod(self, method):
    return isinstance(method, staticmethod)
    
  def getMockFor(self, cls):
    return self.static_mocks[cls]
  
  def accepts(self, obj):
    return inspect.ismodule(obj) or isinstance(obj, types.ClassType)
  
  def unstub(self):
    while self.originals:
      original_method, invocation = self.originals.pop()
      invocation.replaceMethod(original_method)
