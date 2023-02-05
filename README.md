# ldap-acl-broker
Open Service Broker for LDAP-ACL-Milter

Related reading: https://github.com/openservicebrokerapi/servicebroker/blob/master/spec.md!

# LDAP schema
Depends on:
* lamPolicy schema: https://github.com/chillout2k/ldap-acl-milter/blob/devel/LDAP/ldap-acl-milter.schema
* COSINE schema - especially the `simpleSecurityObject`-attribute: https://www.ietf.org/rfc/rfc1274.txt - 

# Developing
## Prepare env
```
export LDAP_URI=ldap://###
export LDAP_BINDDN=uid=###
export LDAP_BINDPW=###
export LDAP_BASE=ou=lam,ou=services,dc=zwackl,dc=de
```
## provision
```
curl -s -u 'blah:blubb' \
  127.0.0.1:5000/v2/service_instances/212b4073-242a-479f-9b7e-034fd9f76287 \
  -H "Content-Type: application/json" \
  -H "X-Broker-API-Version: 2.14" \
  -X PUT -d '{"service_id": "cd6ae21b-9998-4215-a15f-11151868a9fa", "plan_id": "9a0b6927-99b9-4e5f-8e39-1bb603f860da", "organization_guid": "abc", "space_guid": "xyz", "parameters": {"sender_email_address": "blubb@home.arpa"}}'
```

## deprovision
```
curl -s -v -u 'blah:blubb' \
  -X DELETE '127.0.0.1:5000/v2/service_instances/212b4073-242a-479f-9b7e-034fd9f76287?service_id=cd6ae21b-9998-4215-a15f-11151868a9fa&plan_id=9a0b6927-99b9-4e5f-8e39-1bb603f860da' \
  -H "Content-Type: application/json" \
  -H "X-Broker-API-Version: 2.14"
```

## binding
```
curl -s -v -u 'blah:blubb' \
  -X PUT 127.0.0.1:5000/v2/service_instances/212b4073-242a-479f-9b7e-034fd9f76287/service_bindings/some_binding_id \
  -H "Content-Type: application/json" \
  -H "X-Broker-API-Version: 2.14" \
  -d '{"service_id": "cd6ae21b-9998-4215-a15f-11151868a9fa", "plan_id": "9a0b6927-99b9-4e5f-8e39-1bb603f860da"}'
```