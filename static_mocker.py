class StaticMocker():
  
  def __init__(self):
    self.stubbed_statics = []
    self.static_mocks = {}
    
  def stub(self, invocation):
    self.static_mocks[invocation.mock.mocked] = invocation.mock
    def f(*params, **named_params): 
      i = invocation.mock.__getattr__(invocation.method_name)
      return i.__call__(*params, **named_params)
      
    s = (invocation.mock.mocked, getattr(invocation.mock.mocked, invocation.method_name))
    self.stubbed_statics.append(s)
    setattr(invocation.mock.mocked, invocation.method_name, staticmethod(f))