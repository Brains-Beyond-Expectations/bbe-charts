"""Sets up Keycloak for bbe after every install and upgrade: the realm, its groups, a client per app and the users
bbe manages.

Every step reads what is already there first, so running it again only adds what is missing and brings bbe's own
clients and users back in line with the chart's values. Users and clients made in Keycloak's console are left alone.
Only the Python standard library is used, so the job runs on the plain python image.
"""

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

KEYCLOAK_URL = os.environ.get("KEYCLOAK_URL", "").rstrip("/")
# The service account Keycloak creates on its first start, in the master realm
SETUP_CLIENT_ID = os.environ.get("SETUP_CLIENT_ID", "")
SETUP_CLIENT_SECRET = os.environ.get("SETUP_CLIENT_SECRET", "")
REALM = os.environ.get("REALM", "bbe")
# The clients bbe creates, with their secrets as files in CLIENT_SECRETS_DIR
CLIENTS = json.loads(os.environ.get("CLIENTS") or "[]")
CLIENT_SECRETS_DIR = os.environ.get("CLIENT_SECRETS_DIR", "/client-secrets")
# The users bbe creates, from `bbe configure`, with their first passwords as files in USER_PASSWORDS_DIR named in
# their `secretFields`
USERS = json.loads(os.environ.get("USERS") or "[]")
USER_PASSWORDS_DIR = os.environ.get("USER_PASSWORDS_DIR", "/user-passwords")
READY_TIMEOUT = int(os.environ.get("READY_TIMEOUT", "900"))

# The groups bbe creates, and decides who is in for the users it manages
GROUPS = ["admins", "users"]
# Marks the users bbe created, so it only ever changes or removes its own
BBE_ATTRIBUTE = "bbe"
BBE_MANAGED = "managed"
# The client scope that puts a user's groups in their tokens, as `groups`
GROUPS_SCOPE = "groups"


class SetupError(Exception):
    pass


def log(message):
    print(message, flush=True)


class Keycloak:
    """Keycloak's admin API, signed in as the setup's service account"""

    def __init__(self, url):
        self.url = url
        self.token = ""

    def request(self, method, path, body=None, form=None, timeout=60):
        headers = {"Accept": "application/json"}
        data = None
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        if body is not None:
            data = json.dumps(body).encode()
            headers["Content-Type"] = "application/json"
        elif form is not None:
            data = urllib.parse.urlencode(form).encode()
            headers["Content-Type"] = "application/x-www-form-urlencoded"

        request = urllib.request.Request(self.url + path, data=data, method=method, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                status, content, location = response.status, response.read(), response.headers.get("Location", "")
        except urllib.error.HTTPError as error:
            status, content, location = error.code, error.read(), ""
        except (urllib.error.URLError, OSError) as error:
            raise SetupError(f"Keycloak: {method} {path} failed: {error}")

        if status >= 300:
            raise SetupError(f"Keycloak: {method} {path} returned {status}: {content[:500].decode(errors='replace')}")
        if location:
            # Keycloak answers a creation with the new resource's address, whose last part is its id
            return location.rstrip("/").rsplit("/", 1)[-1]
        return json.loads(content) if content else None

    def get(self, path):
        return self.request("GET", path)

    def post(self, path, body=None, form=None):
        return self.request("POST", path, body=body, form=form)

    def put(self, path, body):
        return self.request("PUT", path, body=body)

    def delete(self, path, body=None):
        return self.request("DELETE", path, body=body)

    def wait_until_ready(self, deadline):
        """Waits until Keycloak answers, as it takes a while to start, then signs in"""
        last_error = "no answer yet"
        while time.monotonic() < deadline:
            try:
                self.sign_in()
                return
            except SetupError as error:
                last_error = str(error)
            time.sleep(5)

        raise SetupError(f"Keycloak wasn't ready after {READY_TIMEOUT} seconds: {last_error}")

    def sign_in(self):
        self.token = ""
        response = self.post("/realms/master/protocol/openid-connect/token", form={
            "grant_type": "client_credentials",
            "client_id": SETUP_CLIENT_ID,
            "client_secret": SETUP_CLIENT_SECRET,
        })
        self.token = response["access_token"]


def read_file(directory, name):
    if not name:
        return ""
    path = os.path.join(directory, name)
    try:
        with open(path) as file:
            return file.read().strip()
    except FileNotFoundError:
        return ""


def configure_realm(keycloak):
    """Creates the realm once. Its settings are left to Keycloak's console after that"""
    if any(realm["realm"] == REALM for realm in keycloak.get("/admin/realms")):
        return

    keycloak.post("/admin/realms", {
        "realm": REALM,
        "enabled": True,
        # People are added by an admin, and there's no mail server to reset a password with
        "registrationAllowed": False,
        "resetPasswordAllowed": False,
        "loginWithEmailAllowed": True,
        "duplicateEmailsAllowed": False,
        "rememberMe": True,
        "bruteForceProtected": True,
        # Behind Traefik every request arrives over HTTPS, and Keycloak only allows plain HTTP from private addresses
        "sslRequired": "external",
    })
    log(f"Keycloak: created the {REALM} realm")


def configure_user_profile(keycloak):
    """Lets admins see the attribute marking bbe's users, which Keycloak drops unless the user profile allows it"""
    profile = keycloak.get(f"/admin/realms/{REALM}/users/profile")
    if any(attribute["name"] == BBE_ATTRIBUTE for attribute in profile.get("attributes", [])):
        return

    profile.setdefault("attributes", []).append({
        "name": BBE_ATTRIBUTE,
        "displayName": "Managed by bbe",
        "permissions": {"view": ["admin"], "edit": ["admin"]},
        "multivalued": False,
    })
    keycloak.put(f"/admin/realms/{REALM}/users/profile", profile)
    log(f"Keycloak: added the `{BBE_ATTRIBUTE}` attribute to the user profile")


def configure_groups(keycloak):
    """Creates the groups, and lets admins manage the realm, its users included, in Keycloak's console"""
    existing = {group["name"]: group["id"] for group in keycloak.get(f"/admin/realms/{REALM}/groups?briefRepresentation=true&max=1000")}
    for name in GROUPS:
        if name not in existing:
            existing[name] = keycloak.post(f"/admin/realms/{REALM}/groups", {"name": name})
            log(f"Keycloak: created the {name} group")

    management = keycloak.get(f"/admin/realms/{REALM}/clients?clientId=realm-management")[0]
    mappings = keycloak.get(f"/admin/realms/{REALM}/groups/{existing['admins']}/role-mappings/clients/{management['id']}")
    if not any(role["name"] == "realm-admin" for role in mappings):
        role = keycloak.get(f"/admin/realms/{REALM}/clients/{management['id']}/roles/realm-admin")
        keycloak.post(f"/admin/realms/{REALM}/groups/{existing['admins']}/role-mappings/clients/{management['id']}", [role])
        log("Keycloak: admins can manage the realm")

    return existing


def configure_groups_scope(keycloak):
    """A client scope putting a user's groups in their tokens and user info, by name, as `groups`"""
    scopes = keycloak.get(f"/admin/realms/{REALM}/client-scopes")
    scope = next((scope for scope in scopes if scope["name"] == GROUPS_SCOPE), None)
    if scope is not None:
        return scope["id"]

    scope_id = keycloak.post(f"/admin/realms/{REALM}/client-scopes", {
        "name": GROUPS_SCOPE,
        "description": "The user's groups, such as admins",
        "protocol": "openid-connect",
        "attributes": {"include.in.token.scope": "true", "display.on.consent.screen": "false"},
        "protocolMappers": [{
            "name": "groups",
            "protocol": "openid-connect",
            "protocolMapper": "oidc-group-membership-mapper",
            "config": {
                "claim.name": "groups",
                "full.path": "false",
                "id.token.claim": "true",
                "access.token.claim": "true",
                "userinfo.token.claim": "true",
            },
        }],
    })
    log(f"Keycloak: created the {GROUPS_SCOPE} client scope")
    return scope_id


def client_representation(client, secret):
    """What bbe sets on one of its clients, from the chart's values"""
    representation = {
        "clientId": client["clientId"],
        "name": client.get("name", client["clientId"]),
        "enabled": True,
        "protocol": "openid-connect",
        "publicClient": False,
        "secret": secret,
        "standardFlowEnabled": True,
        "directAccessGrantsEnabled": False,
        "implicitFlowEnabled": False,
        "serviceAccountsEnabled": False,
        "rootUrl": client.get("rootUrl", ""),
        "baseUrl": client.get("baseUrl", ""),
        "redirectUris": client["redirectUris"],
        "attributes": {"post.logout.redirect.uris": "+", "pkce.code.challenge.method": "S256"},
    }
    if client.get("audience"):
        # oauth2-proxy checks a token was made for it, which Keycloak only says in `aud` with a mapper
        representation["protocolMappers"] = [{
            "name": "audience",
            "protocol": "openid-connect",
            "protocolMapper": "oidc-audience-mapper",
            "config": {
                "included.client.audience": client["clientId"],
                "id.token.claim": "true",
                "access.token.claim": "true",
            },
        }]
    return representation


def configure_clients(keycloak, groups_scope):
    existing = {client["clientId"]: client for client in keycloak.get(f"/admin/realms/{REALM}/clients?max=1000")}
    for client in CLIENTS:
        secret = read_file(CLIENT_SECRETS_DIR, client["clientId"])
        if not secret:
            raise SetupError(f"Keycloak: the secret of client {client['clientId']} is missing")

        representation = client_representation(client, secret)
        current = existing.get(client["clientId"])
        if current is None:
            client_id = keycloak.post(f"/admin/realms/{REALM}/clients", representation)
            log(f"Keycloak: created the {client['clientId']} client")
        else:
            client_id = current["id"]
            # The mappers are kept as they are once the client exists, as the API replaces them separately
            representation.pop("protocolMappers", None)
            keycloak.put(f"/admin/realms/{REALM}/clients/{client_id}", {**current, **representation, "attributes": {**current.get("attributes", {}), **representation["attributes"]}})
            if client.get("audience") and not any(mapper["protocolMapper"] == "oidc-audience-mapper" for mapper in current.get("protocolMappers", [])):
                keycloak.post(f"/admin/realms/{REALM}/clients/{client_id}/protocol-mappers/models", client_representation(client, secret)["protocolMappers"][0])

        scopes = keycloak.get(f"/admin/realms/{REALM}/clients/{client_id}/default-client-scopes")
        if not any(scope["id"] == groups_scope for scope in scopes):
            keycloak.put(f"/admin/realms/{REALM}/clients/{client_id}/default-client-scopes/{groups_scope}", {})
            log(f"Keycloak: {client['clientId']} gets the user's groups")


def configure_users(keycloak, groups):
    """Creates the listed users with a first password they change when they first sign in, keeps them in the groups
    the values give them, and removes the users bbe created that are no longer listed"""
    managed = keycloak.get(f"/admin/realms/{REALM}/users?q={BBE_ATTRIBUTE}:{BBE_MANAGED}&max=10000")
    managed_by_name = {user["username"]: user for user in managed}
    listed = set()

    for user in USERS:
        username = user["username"].lower()
        listed.add(username)
        current = managed_by_name.get(username)
        if current is None:
            if keycloak.get(f"/admin/realms/{REALM}/users?username={urllib.parse.quote(username)}&exact=true"):
                log(f"WARNING Keycloak: there's already a user {username} bbe didn't create, which it leaves alone")
                continue

            password = read_file(USER_PASSWORDS_DIR, user.get("secretFields", {}).get("password", ""))
            if not password:
                raise SetupError(f"Keycloak: the first password of {username} is missing")
            user_id = keycloak.post(f"/admin/realms/{REALM}/users", {
                "username": username,
                "email": user.get("email", ""),
                "emailVerified": bool(user.get("email")),
                "firstName": user.get("firstName", ""),
                "lastName": user.get("lastName", ""),
                "enabled": True,
                "attributes": {BBE_ATTRIBUTE: [BBE_MANAGED]},
                "credentials": [{"type": "password", "value": password, "temporary": True}],
            })
            log(f"Keycloak: created the user {username}, who sets a new password when signing in first")
        else:
            user_id = current["id"]

        # Only bbe's own groups are kept in line, others someone added in the console stay
        wanted = set(user.get("groups", ["users"]))
        member_of = {group["name"] for group in keycloak.get(f"/admin/realms/{REALM}/users/{user_id}/groups?briefRepresentation=true")}
        for name in GROUPS:
            if name in wanted and name not in member_of:
                keycloak.put(f"/admin/realms/{REALM}/users/{user_id}/groups/{groups[name]}", {})
                log(f"Keycloak: added {username} to {name}")
            elif name not in wanted and name in member_of:
                keycloak.delete(f"/admin/realms/{REALM}/users/{user_id}/groups/{groups[name]}")
                log(f"Keycloak: removed {username} from {name}")

    for username, user in managed_by_name.items():
        if username not in listed:
            keycloak.delete(f"/admin/realms/{REALM}/users/{user['id']}")
            log(f"Keycloak: removed the user {username}, who is no longer listed")


def main():
    if not KEYCLOAK_URL or not SETUP_CLIENT_ID or not SETUP_CLIENT_SECRET:
        raise SetupError("KEYCLOAK_URL, SETUP_CLIENT_ID and SETUP_CLIENT_SECRET are required")

    keycloak = Keycloak(KEYCLOAK_URL)
    keycloak.wait_until_ready(time.monotonic() + READY_TIMEOUT)
    log("Keycloak: ready")

    configure_realm(keycloak)
    configure_user_profile(keycloak)
    groups = configure_groups(keycloak)
    groups_scope = configure_groups_scope(keycloak)
    configure_clients(keycloak, groups_scope)
    configure_users(keycloak, groups)
    log("Keycloak is set up")


if __name__ == "__main__":
    try:
        main()
    except SetupError as error:
        log(f"ERROR {error}")
        sys.exit(1)
