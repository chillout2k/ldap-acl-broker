import os
from exceptions import ConfigException

def check_config():
  if 'LDAP_URI' not in os.environ:
    raise ConfigException("ENV[LDAP_URI] is mandatory!")
  print("ENV[LDAP_BINDDN]: {}".format(os.environ['LDAP_URI']))

  if 'LDAP_BINDDN' not in os.environ:
    raise ConfigException("ENV[LDAP_BINDDN] is mandatory!")
  print("ENV[LDAP_BINDDN]: {}".format(os.environ['LDAP_BINDDN']))
  
  if 'LDAP_BINDPW' not in os.environ:
    raise ConfigException("ENV[LDAP_BINDPW] is mandatory!")

  if 'LDAP_BASE' not in os.environ:
    raise ConfigException("ENV[LDAP_BASE] is mandatory!")
  print("ENV[LDAP_BASE]: {}".format(os.environ['LDAP_BASE']))
  
  if 'MAILSERVER_HOST' not in os.environ:
    raise ConfigException("ENV[MAILSERVER_HOST] is mandatory!")
  print("ENV[MAILSERVER_HOST]: {}".format(os.environ['MAILSERVER_HOST']))

  if 'MAILSERVER_PORT' not in os.environ:
    raise ConfigException("ENV[MAILSERVER_PORT] is mandatory!")
  print("ENV[MAILSERVER_PORT]: {}".format(os.environ['MAILSERVER_PORT']))