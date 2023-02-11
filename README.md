# ldap-acl-broker
Open Service Broker API for [LDAP-ACL-Milter](https://github.com/chillout2k/ldap-acl-milter/)

**THIS IS AN EXPERIMENTAL IMPLEMENTATION AND NOT YET READY FOR PRODUCTION-ENVIRONMENTS!!!**

Sits on top of: https://github.com/eruvanos/openbrokerapi

Related reading: 
* https://www.openservicebrokerapi.org/
* https://github.com/openservicebrokerapi/servicebroker/blob/master/spec.md

# Required LDAP schema!
Depends on:
* lamPolicy schema: https://github.com/chillout2k/ldap-acl-milter/blob/devel/LDAP/ldap-acl-milter.schema
* COSINE schema - especially the `simpleSecurityObject`-attribute: https://www.ietf.org/rfc/rfc1274.txt - 

# How to start a local instance
Activate venv:
```
. venv/bin/activate
```
Install all python requirements:
```
pip3 install -r requirements.txt
```
Set config via env-vars:
```
export LDAP_URI=ldaps://your-ldap-server-with-lam-schema
export LDAP_BINDDN=uid=###
export LDAP_BINDPW=###
export LDAP_BASE=ou=lam,ou=services,dc=xyz
export MAILSERVER_HOST=some.mail.relay
export MAILSERVER_PORT=465
export BROKER_USER=blah
export BROKER_PASS=blubb
```
Start broker:
```
python3 app/broker.py
```

# Query the API
The broker provides just one service (cd6ae21b-9998-4215-a15f-11151868a9fa) with one service plan (9a0b6927-99b9-4e5f-8e39-1bb603f860da)


## catalog (return all services and related service plans)
```
curl -s -v -u 'blah:blubb' \
  -X GET \
  -H "Content-Type: application/json" \
  -H "X-Broker-API-Version: 2.14" \
  '127.0.0.1:5000/v2/catalog'
```

## provision (create service instance)
Create a service instance with an `instance_id` of 212b4073-242a-479f-9b7e-034fd9f76287. The `instance_id` comes from the platform calling the broker API and identifies a globally unique service-instance. In this case a LAM-policy gets created with `policyID`=`instance_id`.
```
curl -s -v -u 'blah:blubb' \
  -X PUT \
  -H "Content-Type: application/json" \
  -H "X-Broker-API-Version: 2.14" \
  -d '{"service_id": "cd6ae21b-9998-4215-a15f-11151868a9fa", "plan_id": "9a0b6927-99b9-4e5f-8e39-1bb603f860da", "organization_guid": "some_cloudfoundry_stuff", "space_guid": "some_cloudfoundry_stuff", "parameters": {"sender_email_address": "blubb@home.arpa"}}' \
  '127.0.0.1:5000/v2/service_instances/212b4073-242a-479f-9b7e-034fd9f76287'
```

## bind (generate credentials)
```
curl -s -v -u 'blah:blubb' \
  -X PUT \
  -H "Content-Type: application/json" \
  -H "X-Broker-API-Version: 2.14" \
  -d '{"service_id": "cd6ae21b-9998-4215-a15f-11151868a9fa", "plan_id": "9a0b6927-99b9-4e5f-8e39-1bb603f860da"}' \
  '127.0.0.1:5000/v2/service_instances/212b4073-242a-479f-9b7e-034fd9f76287/service_bindings/some_binding_id'
```

## unbind (remove credentials)
```
curl -s -v -u 'blah:blubb' \
  -X DELETE \
  -H "Content-Type: application/json" \
  -H "X-Broker-API-Version: 2.14" \
  '127.0.0.1:5000/v2/service_instances/212b4073-242a-479f-9b7e-034fd9f76287/service_bindings/some_binding_id?service_id=cd6ae21b-9998-4215-a15f-11151868a9fa&plan_id=9a0b6927-99b9-4e5f-8e39-1bb603f860da'
```

## deprovision (remove service instance)
```
curl -s -v -u 'blah:blubb' \
  -X DELETE \
  -H "Content-Type: application/json" \
  -H "X-Broker-API-Version: 2.14" \
  '127.0.0.1:5000/v2/service_instances/212b4073-242a-479f-9b7e-034fd9f76287?service_id=cd6ae21b-9998-4215-a15f-11151868a9fa&plan_id=9a0b6927-99b9-4e5f-8e39-1bb603f860da'
```