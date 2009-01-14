import matchers
import static_mocker
import verification
from mock import Mock
from verification import VerificationError

class ArgumentError(Exception):
  pass

def verify(obj, times=1, atLeast=None, atMost=None, between=None):
# TODO: refactor this mess below...  
  if times < 0:
    raise ArgumentError("'times' argument has invalid value. It should be at least 0. You wanted to set it to: " + str(times))
  if len(filter(lambda x: x, [atLeast, atMost, between])) > 1:
    raise ArgumentError("Sure you know what you are doing? You can set only one of the arguments: 'atLeast', 'atMost' or 'between'.")
  if (atLeast and atLeast < 1) or atLeast == 0:
    raise ArgumentError("'atLeast' argument has invalid value. It should be at least 1.  You wanted to set it to: " + str(atLeast))
  if (atMost and atMost < 1) or atMost == 0:
    raise ArgumentError("'atMost' argument has invalid value. It should be at least 1.  You wanted to set it to: " + str(atMost))
  if between:
    start, end = between
    if start > end or start < 0:
      raise ArgumentError("'between' argument has invalid value. It should be both positive values with second number not greater than first e.g. [1, 4] or [0, 3] or [2, 2].  You wanted to set it to: " + str(between))
   
  if static_mocker.INSTANCE.accepts(obj): mock = static_mocker.INSTANCE.getMockFor(obj)  
  else: mock = obj
  
  if atLeast:
    mock.verification = verification.AtLeast(atLeast)
  elif atMost:
    mock.verification = verification.AtMost(atMost)
  elif between:
    mock.verification = verification.Between(*between)
  else:
    mock.verification = verification.Times(times)
  return mock

def times(count):
  return count

def when(obj):
  #TODO verify obj is a class or a mock
  
  mock = obj
  if (static_mocker.INSTANCE.accepts(obj)):
    mock = Mock()
    mock.mocked_obj = obj

  mock.expect_stubbing()
  return mock

def unstub():
  """Unstubs all stubbed static methods and class methods"""
  
  static_mocker.INSTANCE.unstub()

def verifyNoMoreInteractions(*mocks):
  for mock in mocks:
    for i in mock.invocations:
      if not i.verified:
        raise VerificationError("\nUnwanted interaction: " + str(i))
      
def verifyZeroInteractions(*mocks):
  verifyNoMoreInteractions(*mocks)
      
def any(wanted_type=None):
  """Matches any() argument OR any(SomeClass) argument
     Examples:
       when(mock).foo(any()).thenReturn(1)
       verify(mock).foo(any(int))
  """

  return matchers.Any(wanted_type)     
        
def contains(sub):
  return matchers.Contains(sub)