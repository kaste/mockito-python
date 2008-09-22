class MethodPrinter:
  def printIt(self, method_name, *params):
    m = method_name + "("
    for p in params:
      m += self.to_str(p) + ", "
    #TODO be smarter here, a search and replace?      
    return m.rstrip(", ") + ")"
  
  def to_str(self, obj):
    if str == type(obj): return "'" + obj + "'"
    else: return str(obj)