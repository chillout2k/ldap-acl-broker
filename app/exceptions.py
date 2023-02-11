class LABException(Exception):
  id = None
  message = None
  def __init__(self, message):
    self.message = message

  def __str__(self):
    return self.message

class ConfigException(LABException):
  pass

class AlreadyExistsException(LABException):
  pass

class NotFoundException(LABException):
  pass

class BackendException(LABException):
  pass
