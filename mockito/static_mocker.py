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

    mock.replace_method(method_name, original_method)
    
  def register(self, mock):
    self.static_mocks[mock.mocked_obj] = mock
        
  def mock_for(self, cls):
    return self.static_mocks.get(cls, None)
  
  def unstub(self):
    while self.originals:
      mock, method_name, original_method = self.originals.pop()
      mock.set_method(method_name, original_method)
    self.static_mocks.clear()

static_mocker = StaticMocker()