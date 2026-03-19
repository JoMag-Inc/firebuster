# Securing FastAPI REST Services with JWT and Keycloak IdP

This guide provides example of integrating REST services with Keycloak Identity and Access Management to provide stateless Authentication and Authorization Services.

## Configuring the Keycloak Server

Keycloak can be started in multiple ways: [Keycloak Getting Started guides](https://github.com/keycloak/keycloak?tab=readme-ov-file#getting-started). Here, we'll use the easiest option :-)

- We'll use pre-configured realm and user data
- Download the latest release, unzip and copy the folder [import](kcdb/data/import) to the data folder in your unzipped directory.
- From that directory, run the command:

```shell
# this starts all services, keycloak is one of them
docker compose up -d
```

Point your url to: http://localhost:8080 and log in as the `admin` user to access the Keycloak Administration Console. This needs a username and a password.

## .ENV credentials

to be able to commuinicate with the keycloak server we need to define some .env variables: client_id, realm, server_url
If you have no, set up a .env file in root. It should

```env
client_id=
realm=
server_url=
```

## RestAPI Endpoints

There are different endpoints exposed by the service:

- http://localhost:8000/api/v1/public - can be invoked by any user
- http://localhost:8000/api/v1/admin - can be invoked by users with the `ADMIN` role (realm/global)
- http://localhost:8000/api/v1/admin/service - can be invoked by users with the `APP_ADMIN` role (client)
- http://localhost:8000/api/v1/protected - can be invoked by users with the `USER` role (realm/global)
- http://localhost:8000/api/v1/protected/service - can be invoked by users with the `APP_USER` role (client)
- http://localhost:8000/api/v1/protected/{location} - can be invoked by users with the `APP_USER` role and with attribute {location} as path parameter as specified in the scope
- http://localhost:8000/api/v1/ - can be invoked by users with the `APP_USER` role and with attribute {location} as query parameter (e.g., api/v1/?loc=bergen)

To access the resources at the protected endpoints using a JWT bearer token, your client needs to obtain an OAuth2 access token from the Keycloak IdP server.
For this demo, we will obtain tokens using the resource owner password grant type.

You should be able to obtain tokens for any of these users:

| Username  | Password | Roles            | Scope                    |
| --------- | -------- | ---------------- | ------------------------ |
| fireadmin | secret   | ADMIN, APP_ADMIN | firegaurd_location_scope |
| fireuser  | secret   | USER, APP_USER   | firegaurd_location_scope |

To obtain the auth JWT bearer token, use curl as below (Linux/Mac) or other relevant client (e.g., Postman):

```shell
export token=$(\
curl -X POST http://localhost:8080/realms/Firebuster/protocol/openid-connect/token \
-d 'client_id=firebuster-api' \
-d 'username=user1&password=user1&grant_type=password'| jq --raw-output '.access_token' \
)
```

(Make sure to have `jq` package installed.)
You can use the same command to obtain tokens on behalf of other users, by changing the `username` and `password` request parameters.

After running the command above, you can now access the `http://localhost:8000/api/v1/admin` endpoint
for the user `user1` with the `ADMIN` role (realm) as follows:

```shell
curl http://localhost:8000/api/v1/admin -H "Authorization: Bearer "$token
```

You should see the following response from the service:

```
{"message":"This is a protected resource for ADMIN role."}
```
