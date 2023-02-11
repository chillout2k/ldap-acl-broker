import sys
import os
from typing import Union, List
from openbrokerapi import api
from openbrokerapi.api import ServiceBroker
from openbrokerapi.catalog import (
  Schemas, ServicePlan
)
from openbrokerapi.service_broker import (
  Service,
  ProvisionDetails,
  ProvisionedServiceSpec,
  DeprovisionDetails,
  DeprovisionServiceSpec,
  BindDetails,
  Binding,
  UnbindDetails,
  UnbindSpec
)
from openbrokerapi.errors import (
  ErrBadRequest, ErrInstanceAlreadyExists, ErrInstanceDoesNotExist, 
  ErrBindingAlreadyExists, ErrBindingDoesNotExist
)
from exceptions import (
  BackendException, ConfigException, AlreadyExistsException, NotFoundException
)
import ldap_backend
import config
import random
import string

try:
  config.check_config()
except ConfigException as e:
  print("ConfigException: {}".format(e))
  sys.exit(1)

g_ldap_conn = None
try:
  g_ldap_conn = ldap_backend.LDAP_BACKEND()
except BackendException as e:
  print("LDAP-EXCEPTION: {}".format(e))
  sys.exit(1)

class EmailPolicyBroker(ServiceBroker):
  service = Service(
    id='cd6ae21b-9998-4215-a15f-11151868a9fa',
    name='Email Policy Broker',
    description='Creates an email policy',
    bindable=True,
    plans=[
      ServicePlan(
        id='9a0b6927-99b9-4e5f-8e39-1bb603f860da',
        name='Free',
        free=True,
        description='All you can send - for free!',
        schemas=Schemas(
          service_instance={
            "create": {
              "parameters": {
                "$schema": "http://json-schema.org/draft-04/schema#",
                "type": "object",
                "properties": {
                  "sender_email_address": {
                    "description": "Senders email address the policy will be bound to",
                    "type": "string"
                  }
                }
              }
            }
          }
        )
      )
    ]
  )

  def check_request_details(self, details_obj):
    if details_obj.service_id != self.service.id:
      raise ErrBadRequest("Unknown service_id:  {}".format(details_obj.service_id))

    plan_found = False
    for plan in self.service.plans:
      if plan.id == details_obj.plan_id:
        plan_found = True
    if not plan_found:
      raise ErrBadRequest("Unknown plan_id: {}".format(details_obj.plan_id))


  def catalog(self) -> Union[Service, List[Service]]:
    return self.service

  def provision(
    self,
    instance_id: str,
    details: ProvisionDetails,
    async_allowed: bool,
    **kwargs
  ) -> ProvisionedServiceSpec:
    # Create service instance
    print("provisionDetails: {}".format(details.__dict__))
    self.check_request_details(details)

    pass_before_bind = 'not_bound_yet_'.join(
      random.choice(string.ascii_lowercase + string.digits) for _ in range(8)
    )

    try:
      g_ldap_conn.add_policy(
        instance_id,
        {
          "sender_email_address": details.parameters['sender_email_address'],
          "pass_before_bind": pass_before_bind
        }
      )
    except AlreadyExistsException as e:
      raise ErrInstanceAlreadyExists() from e
    except BackendException as e:
      raise ErrBadRequest("provision(): {}".format(e)) from e

    return ProvisionedServiceSpec(
      dashboard_url="https://blah.blubb/{}".format(instance_id)
    )

  def deprovision(
    self,
    instance_id: str,
    details: DeprovisionDetails,
    async_allowed: bool,
    **kwargs
  ) -> DeprovisionServiceSpec:
    # Delete service instance
    print("DeprovisionDetails: {}".format(details.__dict__))
    self.check_request_details(details)
    
    try:
      g_ldap_conn.delete_policy(instance_id)
    except NotFoundException as e:
      raise ErrInstanceDoesNotExist() from e
    except BackendException as e:
      raise ErrBadRequest("deprovision(): {}".format(e)) from e

    return DeprovisionServiceSpec(is_async=False)

  def bind(
    self, 
    instance_id: str, 
    binding_id: str, 
    details: BindDetails, 
    async_allowed: bool, 
    **kwargs
  ) -> Binding:
    self.check_request_details(details)
    print("bind details: {}".format(details.__dict__))

    gen_user_id = ''.join(
      random.choice(string.ascii_lowercase + string.digits) for _ in range(8)
    )

    pass_after_bind = ''.join(
      random.choice(
        string.ascii_lowercase + string.digits + string.ascii_uppercase + string.punctuation
      ) for _ in range(16)
    )

    try:
      if g_ldap_conn.is_user_id(instance_id):
        raise ErrBindingAlreadyExists()

      g_ldap_conn.set_credentials(
        instance_id, 
        {
          "user_id": gen_user_id,
          "user_pass": pass_after_bind
        }
      )
    except NotFoundException as e:
      raise ErrInstanceDoesNotExist() from e
    except BackendException as e:
      raise ErrBadRequest("bind(): {}".format(e)) from e

    return Binding(
      credentials={
        "tls": True,
        "tls_condition": "MUST",
        "user_id": gen_user_id,
        "user_pass": pass_after_bind,
        "host": os.environ['MAILSERVER_HOST'],
        "port": os.environ['MAILSERVER_PORT']
      }
    )

  def unbind(
    self, 
    instance_id: str, 
    binding_id: str, 
    details: UnbindDetails, 
    async_allowed: bool, 
    **kwargs
  ) -> UnbindSpec:
    self.check_request_details(details)

    try:
      if g_ldap_conn.is_user_id(instance_id) == False:
        raise ErrBindingDoesNotExist()

      pass_after_unbind = 'unbound_'.join(
        random.choice(
          string.ascii_lowercase + string.digits + string.ascii_uppercase + string.punctuation
        ) for _ in range(16)
      )

      g_ldap_conn.set_credentials(
        instance_id, 
        {
          "user_id": '',
          "user_pass": pass_after_unbind
        }
      )
    except NotFoundException as e:
      raise ErrInstanceDoesNotExist() from e
    except BackendException as e:
      raise ErrBadRequest("bind(): {}".format(e)) from e

    return UnbindSpec(is_async=False)

print('Start server on 127.0.0.1:5000')

# Simply start the server
api.serve(EmailPolicyBroker(), api.BrokerCredentials(
  os.environ['BROKER_USER'], os.environ['BROKER_PASS']
))
