import os

from ldap3 import (
  Server, Connection, NONE, set_config_parameter, MODIFY_REPLACE
)
from ldap3.core.exceptions import (
  LDAPException, LDAPEntryAlreadyExistsResult, LDAPNoSuchObjectResult
)

from exceptions import (
  BackendException, AlreadyExistsException, NotFoundException
)

class LDAP_BACKEND:
  def __init__(self):
    self.ldap_conn = None
    self.connect()

  def connect(self):
    try:
      set_config_parameter("RESTARTABLE_SLEEPTIME", 2)
      set_config_parameter("RESTARTABLE_TRIES", 3)
      set_config_parameter('DEFAULT_SERVER_ENCODING', 'utf-8')
      set_config_parameter('DEFAULT_CLIENT_ENCODING', 'utf-8')
      server = Server(os.environ['LDAP_URI'], get_info=NONE)
      self.ldap_conn = Connection(server,
        os.environ['LDAP_BINDDN'],
        os.environ['LDAP_BINDPW'],
        auto_bind=True, 
        raise_exceptions=True,
        client_strategy='RESTARTABLE'
      )
      print("LDAP-Connection steht. PID: " + str(os.getpid()))
    except LDAPException as e:
      raise BackendException("LDAP Exception: {}".format(e)) from e

  def add_policy(self, instance_id, policy_dict):
    try:
      self.ldap_conn.add(
        "policyId={0},{1}".format(
          instance_id,
          os.environ['LDAP_BASE']
        ), 
        ['lamPolicy', 'simpleSecurityObject'], 
        {
          'policyID': instance_id, 
          'allowedSenders': policy_dict['sender_email_address'],
          'userPassword': 'password-is-set-with-binding'
        }
      )
    except LDAPEntryAlreadyExistsResult as e:
      raise AlreadyExistsException(
        "Policy for instance_id {} already exists".format(instance_id)
      ) from e
    except LDAPException as e:
      raise BackendException("LDAPException: {}".format(e)) from e

  def is_user_id(self, instance_id) -> bool:
    try:
      base = "policyID={0},{1}".format(instance_id, os.environ['LDAP_BASE'])
      self.ldap_conn.search(
        base, 
        "(allowedSaslUser=*)",
        attributes=['allowedSaslUser']
      )
      print("Entries: {}".format(self.ldap_conn.entries))
      if len(self.ldap_conn.entries) == 0:
        return False
      return True
    except LDAPNoSuchObjectResult as e:
      raise NotFoundException("Instance {} not found".format(instance_id)) from e
    except LDAPException as e:
      raise BackendException("set_credentials(): {}".format(e)) from e

  def set_credentials(self, instance_id, creds_dict):
    try:
      self.ldap_conn.modify(
        "policyId={0},{1}".format(
          instance_id,
          os.environ['LDAP_BASE']
        ),
        {
          'allowedSaslUser': [(MODIFY_REPLACE, [creds_dict['user_id']])],
          'userPassword': [(MODIFY_REPLACE, [creds_dict['user_pass']])]
        }
      )
    except LDAPNoSuchObjectResult as e:
      raise NotFoundException("Instance {} not found".format(instance_id)) from e
    except LDAPException as e:
      raise BackendException("set_credentials(): {}".format(e)) from e


  def delete_policy(self, instance_id):
    try:
      self.ldap_conn.delete(
        "policyId={0},{1}".format(
          instance_id,
          os.environ['LDAP_BASE']
        )
      )
    except LDAPNoSuchObjectResult as e:
      raise NotFoundException("Instance {} not found".format(instance_id)) from e
    except LDAPException as e:
      raise BackendException("delete_policy(): {}".format(e)) from e
