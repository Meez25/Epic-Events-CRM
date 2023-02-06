# Epic-Events-CRM

## Endpoints

### For sales user
with a filter to only see the customer who the user manage

- /customer/ POST
- /customer/ GET
- /customer/pk/ GET
- /customer/pk/ PUT
- /customer/pk/ PATCH

- /customer/?mail=example@example.com GET
- /customer/?name=example GET

- /customer/pk/contract/ GET
- /customer/pk/contract/ POST
- /customer/pk/contract/pk/ PUT
- /customer/pk/contract/pk/ PATCH

- /customer/pk/contract/?name=example GET
- /customer/pk/contract/?mail=example@example.com GET
- /customer/pk/contract/?date=01-01-2023 GET
- /customer/pk/contract/?amount=550 GET

- /customer/pk/contract/pk/event/ GET
- /customer/pk/contract/pk/event/ POST
- /customer/pk/contract/pk/event/pk/ GET

- /customer/pk/contract/pk/event/?name=example GET
- /customer/pk/contract/pk/event/?mail=example@example.com GET
- /customer/pk/contract/pk/event/?eventdate=28-02-2023 GET


### For support 
with a filter to only see the customer who has an event managed by the user

- /customer/ GET 
- /customer/pk/ GET

- /customer/?mail=example@example.com GET
- /customer/?name=example GET

- /customer/pk/contract/ GET

- /customer/pk/contract/?name=example GET
- /customer/pk/contract/?mail=example@example.com GET
- /customer/pk/contract/?date=01-01-2023 GET
- /customer/pk/contract/?amount=550 GET

- /customer/pk/contract/pk/event/ GET
- /customer/pk/contract/pk/event/pk/ GET
- /customer/pk/contract/pk/event/pk/ PUT
- /customer/pk/contract/pk/event/pk/ PATCH

- /customer/pk/contract/pk/event/?name=example GET
- /customer/pk/contract/pk/event/?mail=example@example.com GET
- /customer/pk/contract/pk/event/?eventdate=28-02-2023 GET
