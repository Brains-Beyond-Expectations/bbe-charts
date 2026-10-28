"""Sets up Calibre-Web-Automated for bbe after every install and upgrade: its own admin, the library the chart created,
signing people in against authentik's LDAP, Kobo sync, what new people may do, and admin rights for authentik's
`admins`. With MODE=people, as the chart's CronJob runs it, it only keeps people in line: admin rights, and their
Send to eReader address, for those Calibre-Web created on their first sign-in.

Calibre-Web has no API for its settings, so this signs in like a browser and posts its admin forms back with what it
changes. A form saves every field it's sent, and an unticked checkbox isn't sent, so each form is read first and sent
back whole. Every step reads what's already there first, so running it again changes nothing. It runs on the
Calibre-Web-Automated image, for its python-ldap.
"""

import html.parser
import http.cookiejar
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

import ldap

CALIBRE_URL = os.environ.get("CALIBRE_URL", "").rstrip("/")
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")
LDAP_SERVER = os.environ.get("LDAP_SERVER", "")
LDAP_PORT = int(os.environ.get("LDAP_PORT", "389"))
LDAP_BASE_DN = os.environ.get("LDAP_BASE_DN", "dc=ldap,dc=goauthentik,dc=io")
LDAP_BIND_DN = os.environ.get("LDAP_BIND_DN", "")
LDAP_PASSWORD = os.environ.get("LDAP_PASSWORD", "")
EXTERNAL_PORT = os.environ.get("EXTERNAL_PORT", "443")
READY_TIMEOUT = int(os.environ.get("READY_TIMEOUT", "900"))
# `setup` sets everything up, `people` only keeps people in line
MODE = os.environ.get("MODE", "setup")

# Calibre-Web's first start creates this admin, which bbe renames and gives its own password
DEFAULT_ADMIN = ("admin", "admin123")
# The library the chart's folders Job created on the share, as the chart's dirs.json names it
LIBRARY_DIR = os.environ.get("LIBRARY_DIR", "/share/books")
# The groups people sign in with, and the one whose members are the library's admins
GROUPS = ["users", "admins"]
ADMIN_GROUP = "admins"
ROLE_ADMIN = 1
# What people may do when they first sign in: download, read in the browser and keep shelves. Admins also upload,
# edit and delete
DEFAULT_ROLES = ["download_role", "viewer_role", "edit_shelf_role"]


class SetupError(Exception):
    pass


def log(message):
    print(message, flush=True)


def group_dn(group):
    return f"cn={group},ou=groups,{LDAP_BASE_DN}"


class Forms(html.parser.HTMLParser):
    """The fields of every form on a page, as a browser would post them"""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.forms = []
        # Every field each form has, sent or not, as unticked checkboxes aren't
        self.names = []
        self.fields = None
        self.select = None
        self.option = None
        self.textarea = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "form":
            self.fields = []
            self.forms.append(self.fields)
            self.names.append(set())
        if self.fields is None:
            return
        name = attrs.get("name")
        if name and tag in ("input", "select", "textarea"):
            self.names[-1].add(name)
        if "disabled" in attrs:
            return
        if tag == "input" and name:
            kind = attrs.get("type", "text").lower()
            if kind in ("checkbox", "radio"):
                if "checked" in attrs:
                    self.fields.append((name, attrs.get("value") or "on"))
            elif kind not in ("submit", "button", "file", "image", "reset"):
                self.fields.append((name, attrs.get("value") or ""))
        elif tag == "select" and name:
            self.select = {"name": name, "first": None, "selected": None}
        elif tag == "option" and self.select is not None:
            self.option = attrs.get("value", "")
            if self.select["first"] is None:
                self.select["first"] = self.option
            if "selected" in attrs:
                self.select["selected"] = self.option
        elif tag == "textarea" and name:
            self.textarea = [name, ""]

    def handle_data(self, data):
        if self.textarea is not None:
            self.textarea[1] += data

    def handle_endtag(self, tag):
        if tag == "select" and self.select is not None:
            value = self.select["selected"] if self.select["selected"] is not None else self.select["first"]
            if value is not None:
                self.fields.append((self.select["name"], value))
            self.select = None
        elif tag == "textarea" and self.textarea is not None:
            self.fields.append(tuple(self.textarea))
            self.textarea = None
        elif tag == "form":
            self.fields = None


def form_with(page, field):
    """The form on a page that has a field, as a dict of what a browser would post"""
    parser = Forms()
    parser.feed(page)
    for fields, names in zip(parser.forms, parser.names):
        if field in names:
            values = {}
            for name, value in fields:
                values.setdefault(name, value)
            return values
    raise SetupError(f"Calibre-Web: there's no form with `{field}`")


class InsideTheCluster(http.cookiejar.DefaultCookiePolicy):
    """Sends Calibre-Web's session cookie over plain HTTP too. It's marked secure for people, who reach it over HTTPS,
    and this only talks to its Service inside the cluster"""

    def return_ok_secure(self, cookie, request):
        return True


class CalibreWeb:
    """Calibre-Web's pages, signed in with a session cookie like a browser"""

    def __init__(self, url):
        self.url = url
        cookies = http.cookiejar.CookieJar(policy=InsideTheCluster())
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookies))
        self.csrf_token = ""

    def request(self, method, path, form=None, ajax=False, timeout=120):
        headers = {"Accept": "application/json, text/html"}
        data = None
        if form is not None:
            data = urllib.parse.urlencode(form).encode()
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        if ajax:
            headers["X-CSRFToken"] = self.csrf_token
            headers["X-Requested-With"] = "XMLHttpRequest"

        request = urllib.request.Request(self.url + path, data=data, method=method, headers=headers)
        try:
            with self.opener.open(request, timeout=timeout) as response:
                status, final_url, content = response.status, response.url, response.read().decode(errors="replace")
        except urllib.error.HTTPError as error:
            status, final_url, content = error.code, error.url, error.read().decode(errors="replace")
        except (urllib.error.URLError, OSError) as error:
            raise SetupError(f"Calibre-Web: {method} {path} failed: {error}")

        if status >= 400:
            raise SetupError(f"Calibre-Web: {method} {path} returned {status}: {content[:300]}")
        match = re.search(r'name="csrf_token" value="([^"]+)"', content)
        if match:
            self.csrf_token = match.group(1)
        return urllib.parse.urlsplit(final_url).path, content

    def get(self, path):
        return self.request("GET", path)[1]

    def post_form(self, path, form):
        """Posts a form back with the page's CSRF token"""
        return self.request("POST", path, dict(form, csrf_token=self.csrf_token))

    def post_ajax(self, path, form):
        """Its answer, which some endpoints leave empty when they've saved it, and answer errors with 400 otherwise"""
        content = self.request("POST", path, form, ajax=True)[1]
        if not content.strip():
            return {}
        try:
            return json.loads(content)
        except ValueError:
            raise SetupError(f"Calibre-Web: POST {path} didn't answer with JSON: {content[:300]}")

    def wait_until_ready(self, deadline):
        """Waits until the login page answers, which takes a while on the first start as it sets Calibre up"""
        last_error = "no answer yet"
        while time.monotonic() < deadline:
            try:
                self.get("/login")
                return
            except SetupError as error:
                last_error = str(error)
            time.sleep(5)
        raise SetupError(f"Calibre-Web wasn't ready after {READY_TIMEOUT} seconds: {last_error}")

    def sign_in(self, username, password):
        """Whether the login worked. A failed login answers with the login page again"""
        self.get("/login")
        path, _ = self.request("POST", "/login", {
            "username": username,
            "password": password,
            "remember_me": "on",
            "next": "/",
            "csrf_token": self.csrf_token,
        })
        return not path.endswith("/login")

    def signed_in(self):
        """Whether the session still holds, which is checked before signing in again: Calibre-Web allows three logins
        a minute for each username"""
        path, _ = self.request("GET", "/admin/alive")
        return not path.endswith("/login")

    def users(self):
        return self.request("GET", "/ajax/listusers?" + urllib.parse.urlencode({"offset": 0, "limit": 10000}))[1]


def check_result(result, what):
    """The admin forms answer with a list of messages, `danger` ones when something wasn't saved"""
    messages = result.get("result", result) if isinstance(result, dict) else result
    for message in messages if isinstance(messages, list) else []:
        if isinstance(message, dict) and message.get("type") == "danger":
            raise SetupError(f"Calibre-Web: {what} wasn't saved: {message.get('message')}")


def sign_in_admin(calibre):
    """Signs in as the library's own admin, or as Calibre-Web's default one before the first run made it bbe's. Says
    whether it's the default one"""
    if calibre.sign_in(ADMIN_USERNAME, ADMIN_PASSWORD):
        return False
    if calibre.sign_in(*DEFAULT_ADMIN):
        return True
    raise SetupError(f"Calibre-Web: neither {ADMIN_USERNAME} nor its default admin could sign in")


def configure_admin(calibre):
    """Makes Calibre-Web's default admin the library's own, with bbe's name and password"""
    users = json.loads(calibre.users())["rows"]
    admin = next((user for user in users if user["name"] == DEFAULT_ADMIN[0]), None)
    if admin is None:
        raise SetupError("Calibre-Web: its default admin isn't in its users")
    form = form_with(calibre.get(f"/admin/user/{admin['id']}"), "password")
    form["password"] = ADMIN_PASSWORD
    calibre.post_form(f"/admin/user/{admin['id']}", form)
    check_result(calibre.post_ajax("/ajax/editlistusers/name", {"pk": admin["id"], "value": ADMIN_USERNAME}),
                 "the admin's name")
    # Checks the new login, as the user form doesn't say what it didn't save. It's the second login with the name
    if not calibre.sign_in(ADMIN_USERNAME, ADMIN_PASSWORD):
        raise SetupError(f"Calibre-Web: {ADMIN_USERNAME} couldn't sign in with its new password")
    log(f"Calibre-Web: its admin is {ADMIN_USERNAME}, with bbe's password")


def configure_library(calibre):
    """Points Calibre-Web at the library the chart's init container created on the share"""
    form = form_with(calibre.get("/admin/dbconfig"), "config_calibre_dir")
    if form.get("config_calibre_dir") == LIBRARY_DIR:
        return
    form["config_calibre_dir"] = LIBRARY_DIR
    calibre.request("POST", "/admin/ajaxdbconfig", dict(form, csrf_token=calibre.csrf_token), ajax=True)
    if form_with(calibre.get("/admin/dbconfig"), "config_calibre_dir").get("config_calibre_dir") != LIBRARY_DIR:
        raise SetupError(f"Calibre-Web: it wasn't pointed at the library in {LIBRARY_DIR}")
    log(f"Calibre-Web: the library is {LIBRARY_DIR}")


def basic_settings():
    """Signing in against authentik's LDAP, for people in `users` or `admins`, Kobo sync and uploads. The library's own
    admin isn't in LDAP, so it keeps signing in with its own password"""
    members = "".join(f"(memberOf={group_dn(group)})" for group in GROUPS)
    return {
        "config_login_type": "1",
        "config_ldap_provider_url": LDAP_SERVER,
        "config_ldap_port": str(LDAP_PORT),
        # Plain LDAP inside the cluster, like Jellyfin's
        "config_ldap_encryption": "0",
        "config_ldap_cacert_path": "",
        "config_ldap_cert_path": "",
        "config_ldap_key_path": "",
        "config_ldap_authentication": "2",
        "config_ldap_serv_username": LDAP_BIND_DN,
        "config_ldap_dn": LDAP_BASE_DN,
        "config_ldap_user_object": f"(&(cn=%s)(|{members}))",
        # Binding takes a user's DN from the search, as authentik's entries have no Active Directory
        # `distinguishedName`. Its groups list their members' DNs in `member`
        "config_ldap_openldap": "on",
        "config_ldap_group_object_filter": "(&(objectClass=group)(cn=%s))",
        "config_ldap_group_members_field": "member",
        "config_ldap_group_name": ADMIN_GROUP,
        "ldap_import_user_filter": "0",
        "config_ldap_auto_create_users": "on",
        # Kobo e-readers sync with the library, which gives them the address they reach it at, through Traefik
        "config_kobo_sync": "on",
        "config_external_port": EXTERNAL_PORT,
        # Admins add books in the browser too, which go to the ingest folder
        "config_uploading": "on",
    }


def configure_basics(calibre, deadline):
    form = form_with(calibre.get("/admin/config"), "config_login_type")
    wanted = basic_settings()
    changed = [name for name, value in wanted.items() if form.get(name) != value]
    if not changed:
        return

    for name, value in wanted.items():
        if value is None:
            form.pop(name, None)
        else:
            form[name] = value
    # Calibre-Web keeps the password it has unless it's sent one, and never shows it
    form["config_ldap_serv_password_e"] = LDAP_PASSWORD
    result = calibre.post_ajax("/admin/ajaxconfig", form)
    check_result(result, "the basic settings")
    log(f"Calibre-Web: people sign in with authentik's LDAP, and Kobo sync is on ({', '.join(changed)})")

    # Calibre-Web starts LDAP and Kobo sync when it starts, so it restarts itself for them
    if result.get("reboot"):
        log("Calibre-Web: restarting for its new settings")
        time.sleep(10)
        calibre.wait_until_ready(deadline)
        # The session usually holds, as Calibre-Web keeps its secret key in its database
        if not calibre.signed_in() and not calibre.sign_in(ADMIN_USERNAME, ADMIN_PASSWORD):
            raise SetupError(f"Calibre-Web: {ADMIN_USERNAME} couldn't sign in after it restarted")


def configure_default_roles(calibre):
    """What people may do when Calibre-Web creates them, on their first sign-in"""
    form = form_with(calibre.get("/admin/viewconfig"), "download_role")
    missing = [role for role in DEFAULT_ROLES if form.get(role) != "on"]
    if not missing:
        return
    for role in DEFAULT_ROLES:
        form[role] = "on"
    calibre.post_form("/admin/viewconfig", form)
    log(f"Calibre-Web: new people get {', '.join(DEFAULT_ROLES)}")


def ldap_members(deadline):
    """The usernames in each of bbe's groups, from authentik's LDAP. On a first install its outpost starts answering
    minutes after authentik does, so this waits for it until the deadline"""
    waiting = False
    while True:
        connection = ldap.initialize(f"ldap://{LDAP_SERVER}:{LDAP_PORT}")
        connection.set_option(ldap.OPT_NETWORK_TIMEOUT, 30)
        try:
            connection.simple_bind_s(LDAP_BIND_DN, LDAP_PASSWORD)
            members = {}
            for group in GROUPS:
                found = connection.search_s(LDAP_BASE_DN, ldap.SCOPE_SUBTREE, f"(memberOf={group_dn(group)})", ["cn"])
                members[group] = {entry["cn"][0].decode().lower() for dn, entry in found if dn and entry.get("cn")}
            return members
        except ldap.SERVER_DOWN as error:
            if time.monotonic() > deadline:
                raise SetupError(f"LDAP: authentik's LDAP wasn't answering after {READY_TIMEOUT} seconds: {error}")
            if not waiting:
                log(f"LDAP: waiting for authentik's LDAP: {error}")
                waiting = True
        except ldap.LDAPError as error:
            raise SetupError(f"LDAP: searching authentik's groups failed: {error}")
        finally:
            connection.unbind_s()
        time.sleep(5)


def configure_people(calibre, deadline):
    members = ldap_members(deadline)
    configure_admins(calibre, members)
    configure_ereader_emails(calibre, members)


def configure_admins(calibre, members):
    """Creates authentik's admins in Calibre-Web, and keeps admin rights for exactly them among the people in LDAP.
    Calibre-Web has no admin group of its own, so this follows `admins`, every few minutes with the chart's CronJob"""
    known = {user["name"].lower() for user in json.loads(calibre.users())["rows"]}
    if members[ADMIN_GROUP] - known:
        result = calibre.post_ajax("/import_ldap_users", {})
        log(f"Calibre-Web: importing authentik's admins: {result.get('text', result)}")

    people = set().union(*members.values())
    for user in json.loads(calibre.users())["rows"]:
        name = user["name"].lower()
        if name not in people:
            continue
        wanted = name in members[ADMIN_GROUP]
        if bool(user["role"] & ROLE_ADMIN) == wanted:
            continue
        check_result(calibre.post_ajax("/ajax/editlistusers/role", {
            "pk": user["id"], "field_index": ROLE_ADMIN, "value": "true" if wanted else "false",
        }), f"{name}'s admin rights")
        log(f"Calibre-Web: {name} is {'now' if wanted else 'no longer'} an admin")


def configure_ereader_emails(calibre, members):
    """Sends people's books to their own email address, for those from authentik who have one and haven't set another.
    Calibre-Web makes up `<username>@email.com` for people without one, which isn't an address to send to"""
    people = set().union(*members.values())
    for user in json.loads(calibre.users())["rows"]:
        name = user["name"].lower()
        email = (user.get("email") or "").strip()
        if name not in people or user.get("kindle_mail") or not email or email.lower() == f"{name}@email.com":
            continue
        calibre.post_ajax("/ajax/editlistusers/kindle_mail", {"pk": user["id"], "value": email})
        log(f"Calibre-Web: {name}'s books are sent to their email address")


def main():
    if not all((CALIBRE_URL, ADMIN_USERNAME, ADMIN_PASSWORD, LDAP_SERVER, LDAP_BIND_DN, LDAP_PASSWORD)):
        raise SetupError("CALIBRE_URL, ADMIN_USERNAME, ADMIN_PASSWORD, LDAP_SERVER, LDAP_BIND_DN and LDAP_PASSWORD "
                         "are required")

    deadline = time.monotonic() + READY_TIMEOUT
    calibre = CalibreWeb(CALIBRE_URL)
    calibre.wait_until_ready(deadline)
    log("Calibre-Web: ready")

    if MODE == "people":
        # The setup Job makes the admin, and a CronJob running before it on a first install has nothing to do yet
        if not calibre.sign_in(ADMIN_USERNAME, ADMIN_PASSWORD):
            log(f"Calibre-Web: {ADMIN_USERNAME} can't sign in yet, which the setup Job sets up")
            return
        configure_people(calibre, deadline)
        return

    default_admin = sign_in_admin(calibre)
    # Until it has a library, Calibre-Web sends every admin page to its database settings
    configure_library(calibre)
    if default_admin:
        configure_admin(calibre)
    configure_basics(calibre, deadline)
    configure_default_roles(calibre)
    configure_people(calibre, deadline)
    log("The library is set up")


if __name__ == "__main__":
    try:
        main()
    except SetupError as error:
        log(f"ERROR {error}")
        sys.exit(1)
