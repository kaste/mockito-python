class MethodPrinter:
  def str(self, method_name, *params):
    m = method_name + "("
    for p in params: 
      m += str(p) + ", "
    return m + ")"