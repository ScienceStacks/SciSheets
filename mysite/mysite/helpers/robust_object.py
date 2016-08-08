"""
A RobustObject provides capabilities for copying, migration,
and testing for equivalence. Implied by this is also a capability
to version.
"""

class RobustObjectVersion(object):

  """
  Creates and tests an object version that includes the versions
  of its (recursively) contained objects. All objects versioned
  should either be RobustObjects or built-in types: int, float,
  str, unicode.
  """
  pass

class MigrationAction(object):
  pass


class RobustObject(object):
