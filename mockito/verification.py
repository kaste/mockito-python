class VerificationError(AssertionError):
  pass

class AtLeast(object):
  def __init__(self, wanted_count):
    self.wanted_count = wanted_count
    
  def verify(self, invocation, actual_count):
    if actual_count < self.wanted_count: 
      raise VerificationError("Wanted at least: " + str(self.wanted_count) + ", actual times: " + str(actual_count))
    
class AtMost(object):
  def __init__(self, wanted_count):
    self.wanted_count = wanted_count
    
  def verify(self, invocation, actual_count):
    if actual_count > self.wanted_count: 
      raise VerificationError("Wanted at most: " + str(self.wanted_count) + ", actual times: " + str(actual_count))

class Between(object):
  def __init__(self, wanted_from, wanted_to):
    self.wanted_from = wanted_from
    self.wanted_to = wanted_to
    
  def verify(self, invocation, actual_count):
    if actual_count < self.wanted_from or actual_count > self.wanted_to: 
      raise VerificationError("Wanted between: " + str((self.wanted_from, self.wanted_to)) + ", actual times: " + str(actual_count))
    
class Times(object):
  def __init__(self, wanted_count):
    self.wanted_count = wanted_count
    
  def verify(self, invocation, actual_count):
    if actual_count != self.wanted_count:
      raise VerificationError("\nWanted but not invoked: " + str(invocation))
    elif actual_count != self.wanted_count:
      raise VerificationError("Wanted times: " + str(self.wanted_count) + ", actual times: " + str(actual_count))