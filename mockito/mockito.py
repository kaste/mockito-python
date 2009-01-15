import matchers
import verification
from mock import Mock
from static_mocker import static_mocker
from verification import VerificationError

class ArgumentError(Exception):
  pass

def _multiple_arguments_in_use(*args):
  return len(filter(lambda x: x, args)) > 1    

def _invalid_argument(value):
  return (value is not None and value < 1) or value == 0

def _invalid_between(between):
  if between is not None:
    start, end = between
    if start > end or start < 0:
      return True
  return False

def verify(obj, times=1, atleast=None, atmost=None, between=None):
  if times < 0:
    raise ArgumentError("""'times' argument has invalid value. 
                           It should be at least 0. You wanted to set it to: %i""" % times)
  if _multiple_arguments_in_use(atleast, atmost, between):
    raise ArgumentError("""Sure you know what you are doing?
                           You can set only one of the arguments: 'atleast', 'atmost' or 'between'.""")
  if _invalid_argument(atleast):
    raise ArgumentError("""'atleast' argument has invalid value.
                           It should be at least 1.  You wanted to set it to: %i""" % atleast)
  if _invalid_argument(atmost):
    raise ArgumentError("""'atmost' argument has invalid value.
                           It should be at least 1.  You wanted to set it to: %i""" % atmost)
  if _invalid_between(between):
    raise ArgumentError("""'between' argument has invalid value.
                           It should consist of positive values with second number not greater than first
                           e.g. [1, 4] or [0, 3] or [2, 2]
                           You wanted to set it to: %s""" % between)
   
  if static_mocker.accepts(obj):
    mock = static_mocker.mockfor(obj)
  else:
    mock = obj
  
  if atleast:
    mock.verification = verification.AtLeast(atleast)
  elif atmost:
    mock.verification = verification.AtMost(atmost)
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
  if (static_mocker.accepts(obj)):
    mock = Mock()
    mock.mocked_obj = obj

  mock.expect_stubbing()
  return mock

def unstub():
  """Unstubs all stubbed static methods and class methods"""
  
  static_mocker.unstub()

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