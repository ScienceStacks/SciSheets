'''Utility routines used in SciSheets core. '''

##################################
# Utility Function
#################################
# Verify that exactly one of the two values is non-None
# BUG - handle variable number of arguments
def verifyArgList(*args):
  is_initialized = False
  for k,v in enumerate(args):
    if is_initialized:
      raise er.InternalError("Only specify one of the inputs.")
    if val1 is not None:
      is_initialized = True
  if not is_initialized:
    raise er.InternalError("Must specify one of the inputs.")
