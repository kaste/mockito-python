class StaticMocker():
  
  def __init__(self):
    self.stubbed_statics = []
    self.static_mocks = {}
    
  def stub(self, mock, invocation):
    self.static_mocks[mock.mocked] = mock
    def f(*params, **named_params): 
      i = mock.__getattr__(invocation.method_name)
      return i.__call__(*params, **named_params)
      
    s = (mock.mocked, getattr(mock.mocked, invocation.method_name))
    self.stubbed_statics.append(s)
    setattr(mock.mocked, invocation.method_name, staticmethod(f))