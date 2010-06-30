class VerificationError(AssertionError):
  pass

class AtLeast(object):
  def __init__(self, wanted_count):
    self.wanted_count = wanted_count
    
  def verify(self, invocation, actual_count):
    if actual_count < self.wanted_count: 
      raise VerificationError("Wanted at least: %i, actual times: %i" % (self.wanted_count, actual_count))
    
class AtMost(object):
  def __init__(self, wanted_count):
    self.wanted_count = wanted_count
    
  def verify(self, invocation, actual_count):
    if actual_count > self.wanted_count: 
      raise VerificationError("Wanted at most: %i, actual times: %i" % (self.wanted_count, actual_count))

class Between(object):
  def __init__(self, wanted_from, wanted_to):
    self.wanted_from = wanted_from
    self.wanted_to = wanted_to
    
  def verify(self, invocation, actual_count):
    if actual_count < self.wanted_from or actual_count > self.wanted_to: 
      raise VerificationError("Wanted between: [%i, %i], actual times: %i" % (self.wanted_from, self.wanted_to, actual_count))
    
class Times(object):
  def __init__(self, wanted_count):
    self.wanted_count = wanted_count
    
  def verify(self, invocation, actual_count):
    if actual_count == self.wanted_count:
        return  
    if actual_count == 0:
      raise VerificationError("\nWanted but not invoked: %s" % (invocation))
    else:
      raise VerificationError("\nWanted times: %i, actual times: %i" % (self.wanted_count, actual_count))
      