import inspect
import mock

class StaticMocker:
  """Deals with static methods AND class methods AND with module functions. 
  As they all are just static, procedural-like functions, hence StaticMocker"""
  
  def __init__(self):
    self.originals = []
    self.static_mocks = {}
    
  def stub(self, stubbed_invocation):
    if not self.accepts(stubbed_invocation.mock.mocked_obj):
      return    
      
    self.static_mocks[stubbed_invocation.mock.mocked_obj] = stubbed_invocation.mock
    original_method = stubbed_invocation.get_original_method()
    original = (original_method, stubbed_invocation)
    self.originals.append(original)

    self._replace_method(stubbed_invocation, original_method)
    
  def _replace_method(self, stubbed_invocation, original_method):
    
    def new_mocked_method(*params, **named_params): 
      if self._is_classmethod(original_method) \
        or (inspect.isclass(stubbed_invocation.mock.mocked_obj) and not self._is_staticmethod(original_method)): 
          params = params[1:]
      call = stubbed_invocation.mock.__getattr__(stubbed_invocation.method_name)
      return call(*params, **named_params)
      
    if self._is_staticmethod(original_method):
      stubbed_invocation.replace_method(staticmethod(new_mocked_method))
    elif self._is_classmethod(original_method): 
      stubbed_invocation.replace_method(classmethod(new_mocked_method))
    elif inspect.ismodule(stubbed_invocation.mock.mocked_obj):
      stubbed_invocation.replace_method(new_mocked_method)
    elif inspect.isclass(stubbed_invocation.mock.mocked_obj):
        stubbed_invocation.replace_method(new_mocked_method)  
    else:
      # TODO create decent error. is it necessary? this case is only useful for library debugging        
      raise "Only module functions, static and class methods can be stubbed"  
    
  def _is_classmethod(self, method):
    return isinstance(method, classmethod)
  
  def _is_staticmethod(self, method):
    return isinstance(method, staticmethod)
    
  def mockfor(self, cls):
    return self.static_mocks[cls]
  
  def accepts(self, obj):
    return inspect.ismodule(obj) or inspect.isclass(obj) and not isinstance(obj, mock.Mock)
  
  def unstub(self):
    while self.originals:
      original_method, stubbed_invocation = self.originals.pop()
      stubbed_invocation.replace_method(original_method)
    self.static_mocks.clear()

static_mocker = StaticMocker()