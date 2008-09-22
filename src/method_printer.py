class MethodPrinter:
  def printIt(self, method_name, *params):
    m = method_name + "("
    for p in params:
      m += str(p) + ", "
    #TODO be smarter here, a search and replace?      
    return m.rstrip(", ") + ")"