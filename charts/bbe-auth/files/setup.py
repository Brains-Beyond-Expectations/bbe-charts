"""Sets up authentik for bbe after every install and upgrade: applies bbe's blueprint, has authentik serve bbe's
certificates, gives the LDAP outpost its token, and keeps the people bbe manages in line with the chart's values.

The blueprint holds the groups, the forward auth and LDAP providers and the branding. People added in authentik's
admin interface are left alone: bbe only changes and removes the ones it created, under the `bbe/people` path. Every
step reads what's already there first, so running it again changes nothing. Only the Python standard library is used,
so the job runs on the plain python image.
"""

import json
import os
from hashlib import sha256, sha512
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

# authentik's server over HTTPS, checked with bbe's certificate authority in CA_FILE
AUTHENTIK_URL = os.environ.get("AUTHENTIK_URL", "").rstrip("/")
CA_FILE = os.environ.get("CA_FILE", "")
# The same server in plain HTTP, only talked to on a first install, until it serves bbe's certificate
AUTHENTIK_BOOTSTRAP_URL = os.environ.get("AUTHENTIK_BOOTSTRAP_URL", "").rstrip("/")
# authentik's bootstrap token, which belongs to its own admin
AUTHENTIK_TOKEN = os.environ.get("AUTHENTIK_TOKEN", "")
BLUEPRINT = os.environ.get("BLUEPRINT", "bbe")
# The blueprint as the chart mounts it, whose hash tells when authentik applied this version
BLUEPRINT_FILE = os.environ.get("BLUEPRINT_FILE", "/blueprints/bbe.yaml")
# Where the worker reads it, for the command that shows why it didn't apply
WORKER_BLUEPRINT_FILE = "/blueprints/mounted/cm-bbe-auth-blueprints/bbe.yaml"
# How long an apply may take before it's asked again, or its error counts
APPLY_WAIT = 300
# The LDAP outpost's Deployment signs in to authentik with this token, which authentik generates otherwise
LDAP_OUTPOST = os.environ.get("LDAP_OUTPOST", "bbe LDAP")
LDAP_OUTPOST_TOKEN = os.environ.get("LDAP_OUTPOST_TOKEN", "")
# The people bbe creates, from `bbe configure`, with their first passwords as files in USER_PASSWORDS_DIR named in
# their `secretFields`
USERS = json.loads(os.environ.get("USERS") or "[]")
USER_PASSWORDS_DIR = os.environ.get("USER_PASSWORDS_DIR", "/user-passwords")
READY_TIMEOUT = int(os.environ.get("READY_TIMEOUT", "900"))
# authentik's own certificates, which its worker imports from /certs/<name>, and the setup reads from
# CERTIFICATES_DIR/<name> to tell when it has: its server's, which its default brand serves, and its LDAP outpost's
CERTIFICATES_DIR = os.environ.get("CERTIFICATES_DIR", "/certificates")
SERVER_CERTIFICATE = os.environ.get("SERVER_CERTIFICATE", "bbe-auth-server")
LDAP_CERTIFICATE = os.environ.get("LDAP_CERTIFICATE", "bbe-auth-ldap")
LDAP_PROVIDER = os.environ.get("LDAP_PROVIDER", "bbe LDAP")
# How long the worker may take to import a certificate before it's asked again
DISCOVERY_WAIT = 120

# The groups whose members bbe keeps in line for the people it manages
GROUPS = ["admins", "users"]
# Where bbe keeps the people it creates, which tells them apart from those added in authentik
PEOPLE_PATH = "bbe/people"
# The brand authentik's server serves its certificate for, when no other matches
DEFAULT_BRAND = "authentik-default"
# How authentik marks the keypairs its worker imported from /certs
DISCOVERED = "goauthentik.io/crypto/discovered/%s"


class SetupError(Exception):
    pass


class NotTrusted(SetupError):
    """authentik answered with a certificate bbe's certificate authority didn't sign: its own, until it serves bbe's"""


def log(message):
    print(message, flush=True)


class Authentik:
    """authentik's API, signed in with its bootstrap token. Over HTTPS, its certificate is checked with `context`"""

    def __init__(self, url, token, context=None):
        self.url = url
        self.token = token
        self.context = context

    def request(self, method, path, body=None, timeout=60):
        headers = {"Accept": "application/json", "Authorization": f"Bearer {self.token}"}
        data = None
        if body is not None:
            data = json.dumps(body).encode()
            headers["Content-Type"] = "application/json"

        request = urllib.request.Request(self.url + "/api/v3" + path, data=data, method=method, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=timeout, context=self.context) as response:
                status, content = response.status, response.read()
        except urllib.error.HTTPError as error:
            status, content = error.code, error.read()
        except urllib.error.URLError as error:
            if isinstance(error.reason, ssl.SSLCertVerificationError):
                raise NotTrusted(f"authentik: {method} {path} failed: {error.reason}")
            raise SetupError(f"authentik: {method} {path} failed: {error}")
        except OSError as error:
            raise SetupError(f"authentik: {method} {path} failed: {error}")

        if status >= 300:
            raise SetupError(f"authentik: {method} {path} returned {status}: {content[:500].decode(errors='replace')}")
        return json.loads(content) if content else None

    # `endpoint` rather than `path`, as authentik filters users by a `path` query
    def get(self, endpoint, **query):
        if query:
            endpoint += "?" + urllib.parse.urlencode(query)
        return self.request("GET", endpoint)

    def results(self, endpoint, **query):
        """Every result of a list, across its pages"""
        page, results = 1, []
        while True:
            response = self.get(endpoint, page=page, page_size=100, **query)
            results += response["results"]
            if not response["pagination"]["next"]:
                return results
            page += 1

    def post(self, path, body=None):
        return self.request("POST", path, body if body is not None else {})

    def patch(self, path, body):
        return self.request("PATCH", path, body)

    def delete(self, path):
        return self.request("DELETE", path)


def secure_client():
    return Authentik(AUTHENTIK_URL, AUTHENTIK_TOKEN, ssl.create_default_context(cafile=CA_FILE))


def connect(deadline):
    """authentik over HTTPS, checked with bbe's certificate authority, once it answers with the token, as its first
    start migrates the database for a while. Until the setup has it serve bbe's certificate, on a first install, it
    answers with its own, and the setup talks to it in plain HTTP inside the namespace instead, only to apply the
    blueprint and have it serve bbe's. Returns the client, and whether it's checked"""
    secure = secure_client()
    bootstrap = Authentik(AUTHENTIK_BOOTSTRAP_URL, AUTHENTIK_TOKEN)
    last_error = "no answer yet"
    while time.monotonic() < deadline:
        try:
            secure.get("/core/users/me/")
            return secure, True
        except NotTrusted:
            try:
                bootstrap.get("/core/users/me/")
                log("authentik: doesn't serve bbe's certificate yet, so it's set up in plain HTTP until it does")
                return bootstrap, False
            except SetupError as error:
                last_error = str(error)
        except SetupError as error:
            last_error = str(error)
        time.sleep(5)

    raise SetupError(f"authentik wasn't ready after {READY_TIMEOUT} seconds: {last_error}")


def wait_until_trusted(deadline):
    """Waits until authentik's server serves bbe's certificate, which it looks for every 3 minutes, and returns the
    client checking it"""
    secure = secure_client()
    last_error = "no answer yet"
    while time.monotonic() < deadline:
        try:
            secure.get("/core/users/me/")
            log("authentik: serves bbe's certificate")
            return secure
        except SetupError as error:
            last_error = str(error)
        time.sleep(10)

    raise SetupError(f"authentik didn't serve bbe's certificate after {READY_TIMEOUT} seconds: {last_error}")


def fingerprint(name):
    """The SHA-256 fingerprint of the first certificate in CERTIFICATES_DIR/<name>/tls.crt, as authentik writes it"""
    end = "-----END CERTIFICATE-----"
    with open(os.path.join(CERTIFICATES_DIR, name, "tls.crt"), encoding="utf-8") as file:
        pem = file.read()
    digest = sha256(ssl.PEM_cert_to_DER_cert(pem[:pem.index(end) + len(end)])).hexdigest()
    return ":".join(digest[i:i + 2] for i in range(0, len(digest), 2))


def discover_certificates(authentik):
    """Has the worker import the certificates in /certs now, rather than when a file changes or within the hour"""
    schedules = [schedule for schedule in authentik.results("/tasks/schedules/")
                 if schedule["actor_name"].endswith("certificate_discovery")]
    if not schedules:
        raise SetupError("authentik: there's no schedule importing the certificates in /certs")
    authentik.post(f"/tasks/schedules/{schedules[0]['id']}/send/")


def imported_keypair(authentik, name, deadline):
    """The keypair authentik's worker imported from /certs/<name>, once it holds the certificate cert-manager issued
    last, with its key"""
    wanted = fingerprint(name)
    requested = None
    while time.monotonic() < deadline:
        found = authentik.results("/crypto/certificatekeypairs/", managed=DISCOVERED % name)
        if found and found[0]["fingerprint_sha256"] == wanted and found[0]["private_key_available"]:
            return found[0]
        if requested is None or time.monotonic() - requested > DISCOVERY_WAIT:
            discover_certificates(authentik)
            requested = time.monotonic()
        time.sleep(5)

    raise SetupError(f"authentik: the worker didn't import the certificate in /certs/{name}. The worker's log says why")


def serve_certificates(authentik, deadline):
    """Has authentik's server serve its certificate, through its default brand, and the LDAP outpost serve its own,
    through its provider. The worker imports them again when cert-manager renews them, into the same keypairs"""
    server = imported_keypair(authentik, SERVER_CERTIFICATE, deadline)
    ldap = imported_keypair(authentik, LDAP_CERTIFICATE, deadline)

    brands = authentik.results("/core/brands/", domain=DEFAULT_BRAND)
    if not brands:
        raise SetupError(f"authentik: there's no `{DEFAULT_BRAND}` brand, which its default blueprint creates")
    if brands[0]["web_certificate"] != server["pk"]:
        authentik.patch(f"/core/brands/{brands[0]['brand_uuid']}/", {"web_certificate": server["pk"]})
        log(f"authentik: its server serves the {SERVER_CERTIFICATE} certificate")

    providers = authentik.results("/providers/ldap/", name__iexact=LDAP_PROVIDER)
    if not providers:
        raise SetupError(f"authentik: there's no `{LDAP_PROVIDER}` LDAP provider, which the blueprint creates")
    if providers[0]["certificate"] != ldap["pk"]:
        authentik.patch(f"/providers/ldap/{providers[0]['pk']}/", {"certificate": ldap["pk"]})
        log(f"authentik: the LDAP outpost serves the {LDAP_CERTIFICATE} certificate")


def read_file(directory, name):
    if not name:
        return ""
    try:
        with open(os.path.join(directory, name)) as file:
            return file.read().strip()
    except FileNotFoundError:
        return ""


def apply_blueprint(authentik, deadline):
    """Has the worker apply bbe's blueprint as it is in the chart, rather than whenever it gets to it, and waits until
    authentik says it applied this very content. The worker can only apply it once authentik's default flows are
    there, and an apply takes minutes, as it applies the default blueprints it builds on first. Each request queues
    another apply, so it's only asked again when one seems lost"""
    with open(BLUEPRINT_FILE, encoding="utf-8") as file:
        wanted_hash = sha512(file.read().encode()).hexdigest()

    requested = None
    last_state = "not found yet"
    while time.monotonic() < deadline:
        instances = authentik.results("/managed/blueprints/", name=BLUEPRINT)
        if instances:
            instance = instances[0]
            if instance["last_applied_hash"] == wanted_hash and instance["status"] == "successful":
                log(f"authentik: applied the `{BLUEPRINT}` blueprint")
                return
            last_state = f"{instance['status']}, applied as {instance['last_applied_hash'][:12] or 'nothing'}"
            waited = time.monotonic() - requested if requested is not None else None
            # An error from before the request stands until the apply it queued has run
            if instance["status"] == "error" and waited is not None and waited > APPLY_WAIT:
                raise SetupError(
                    f"authentik: the `{BLUEPRINT}` blueprint didn't apply. To see why: kubectl exec -n bbe-auth "
                    f"deploy/bbe-auth-worker -- ak apply_blueprint --dry-run {WORKER_BLUEPRINT_FILE}")
            if waited is None or waited > APPLY_WAIT:
                authentik.post(f"/managed/blueprints/{instance['pk']}/apply/")
                requested = time.monotonic()
        time.sleep(10)

    raise SetupError(f"authentik: the `{BLUEPRINT}` blueprint wasn't applied, it's {last_state}. The worker's log says why")


def configure_ldap_outpost(authentik):
    """Gives the LDAP outpost the token its Deployment signs in with"""
    outposts = authentik.results("/outposts/instances/", name__iexact=LDAP_OUTPOST)
    if not outposts:
        raise SetupError(f"authentik: there's no `{LDAP_OUTPOST}` outpost, which the blueprint creates")

    identifier = f"ak-outpost-{outposts[0]['pk']}-api"
    if authentik.get(f"/core/tokens/{identifier}/view_key/")["key"] != LDAP_OUTPOST_TOKEN:
        authentik.post(f"/core/tokens/{identifier}/set_key/", {"key": LDAP_OUTPOST_TOKEN})
        log("authentik: the LDAP outpost signs in with bbe's token")


def configure_users(authentik):
    """Creates the listed people with their first password, keeps them in the groups the values give them, and removes
    the people bbe created that are no longer listed"""
    groups = {}
    for name in GROUPS:
        found = authentik.results("/core/groups/", name=name)
        if not found:
            raise SetupError(f"authentik: there's no `{name}` group, which the blueprint creates")
        groups[name] = found[0]["pk"]

    managed = {user["username"]: user for user in authentik.results("/core/users/", path=PEOPLE_PATH)}
    listed = set()

    for person in USERS:
        username = person["username"].lower()
        listed.add(username)
        current = managed.get(username)
        if current is None:
            if authentik.results("/core/users/", username=username):
                log(f"WARNING authentik: there's already a user {username} bbe didn't create, which it leaves alone")
                continue

            password = read_file(USER_PASSWORDS_DIR, person.get("secretFields", {}).get("password", ""))
            if not password:
                raise SetupError(f"authentik: the first password of {username} is missing")
            name = " ".join(part for part in (person.get("firstName"), person.get("lastName")) if part) or username
            current = authentik.post("/core/users/", {
                "username": username,
                "name": name,
                "email": person.get("email", ""),
                "type": "internal",
                "path": PEOPLE_PATH,
                "is_active": True,
            })
            authentik.post(f"/core/users/{current['pk']}/set_password/", {"password": password})
            current = authentik.get(f"/core/users/{current['pk']}/")
            log(f"authentik: created {username}")

        # Only bbe's own groups are kept in line, others someone added in authentik stay
        wanted = set(person.get("groups", ["users"]))
        member_of = {group["name"] for group in current.get("groups_obj", [])}
        for name in GROUPS:
            if name in wanted and name not in member_of:
                authentik.post(f"/core/groups/{groups[name]}/add_user/", {"pk": current["pk"]})
                log(f"authentik: added {username} to {name}")
            elif name not in wanted and name in member_of:
                authentik.post(f"/core/groups/{groups[name]}/remove_user/", {"pk": current["pk"]})
                log(f"authentik: removed {username} from {name}")

    for username, user in managed.items():
        if username not in listed:
            authentik.delete(f"/core/users/{user['pk']}/")
            log(f"authentik: removed {username}, who is no longer listed")


def main():
    if not all((AUTHENTIK_URL, AUTHENTIK_BOOTSTRAP_URL, CA_FILE, AUTHENTIK_TOKEN, LDAP_OUTPOST_TOKEN)):
        raise SetupError("AUTHENTIK_URL, AUTHENTIK_BOOTSTRAP_URL, CA_FILE, AUTHENTIK_TOKEN and LDAP_OUTPOST_TOKEN are "
                         "required")

    deadline = time.monotonic() + READY_TIMEOUT
    authentik, trusted = connect(deadline)
    log("authentik: ready")

    apply_blueprint(authentik, deadline)
    serve_certificates(authentik, deadline)
    # The outpost's token and people's passwords only go to authentik over HTTPS
    if not trusted:
        authentik = wait_until_trusted(deadline)
    configure_ldap_outpost(authentik)
    configure_users(authentik)
    log("authentik is set up")


if __name__ == "__main__":
    try:
        main()
    except SetupError as error:
        log(f"ERROR {error}")
        sys.exit(1)
