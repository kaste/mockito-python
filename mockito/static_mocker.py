import inspect

class StaticMocker:
  """Deals with static methods AND class methods AND with module functions. 
  As they all are just static, procedural-like functions, hence StaticMocker"""
  
  def __init__(self):
    self.originals = []
    self.static_mocks = {}
    
  def stub(self, mock, method_name):
    original_method = mock.get_method(method_name)
    original = (mock, method_name, original_method)
    self.originals.append(original)

    self._replace_method(mock, method_name, original_method)
    
  def _replace_method(self, mock, method_name, original_method):
    
    def new_mocked_method(*args, **kwargs): 
      # we throw away the first argument, if it's either self or cls  
      if inspect.isclass(mock.mocked_obj) and not isinstance(original_method, staticmethod): 
          args = args[1:]
      call = mock.__getattr__(method_name)
      return call(*args, **kwargs)
      

    if isinstance(original_method, staticmethod):
      new_mocked_method = staticmethod(new_mocked_method)  
    elif isinstance(original_method, classmethod): 
      new_mocked_method = classmethod(new_mocked_method)  

    mock.replace_method(method_name, new_mocked_method)
    
  def register(self, mock):
    self.static_mocks[mock.mocked_obj] = mock
        
  def mock_for(self, cls):
    return self.static_mocks.get(cls, None)
  
  def unstub(self):
    while self.originals:
      mock, method_name, original_method = self.originals.pop()
      mock.replace_method(method_name, original_method)
    self.static_mocks.clear()

static_mocker = StaticMocker()