"""Connects the bbe-media apps to each other after every install and upgrade.

Every step reads what is already configured first, so running it again only adds what is missing
and brings bbe's own connections back in line with the chart's secrets. An app whose URL is empty
is skipped. Only the Python standard library is used, so the job runs on the plain python image.
"""

import http.cookiejar
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")
MEDIA_ROOT = os.environ.get("MEDIA_ROOT", "/media")
TV_DIR = os.path.join(MEDIA_ROOT, "tv")
MOVIES_DIR = os.path.join(MEDIA_ROOT, "movies")
DOWNLOADS_DIR = os.path.join(MEDIA_ROOT, "downloads")
READY_TIMEOUT = int(os.environ.get("READY_TIMEOUT", "900"))

JELLYFIN_CLIENT = 'MediaBrowser Client="bbe-media-setup", Device="bbe", DeviceId="bbe-media-setup", Version="1.0.0"'


class SetupError(Exception):
    pass


class App:
    """One app's HTTP API, keeping the session cookies the apps that log in rely on"""

    def __init__(self, name, url, api_key="", headers=None):
        self.name = name
        self.url = url.rstrip("/")
        self.api_key = api_key
        self.headers = headers or {}
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))

    @property
    def host(self):
        return urllib.parse.urlsplit(self.url).hostname

    @property
    def port(self):
        return urllib.parse.urlsplit(self.url).port

    def request(self, method, path, body=None, form=None, headers=None):
        request_headers = {"Accept": "application/json", **self.headers, **(headers or {})}
        data = None
        if body is not None:
            data = json.dumps(body).encode()
            request_headers["Content-Type"] = "application/json"
        elif form is not None:
            data = urllib.parse.urlencode(form).encode()
            request_headers["Content-Type"] = "application/x-www-form-urlencoded"

        request = urllib.request.Request(self.url + path, data=data, method=method, headers=request_headers)
        try:
            with self.opener.open(request, timeout=60) as response:
                status, content = response.status, response.read()
        except urllib.error.HTTPError as error:
            status, content = error.code, error.read()

        if status >= 300:
            raise SetupError(f"{self.name}: {method} {path} returned {status}: {content[:500].decode(errors='replace')}")
        if not content:
            return None
        try:
            return json.loads(content)
        except ValueError:
            return content.decode(errors="replace")

    def get(self, path, **kwargs):
        return self.request("GET", path, **kwargs)

    def post(self, path, body=None, **kwargs):
        return self.request("POST", path, body=body, **kwargs)

    def put(self, path, body=None, **kwargs):
        return self.request("PUT", path, body=body, **kwargs)

    def wait_until_ready(self, path, deadline):
        """Waits until the app answers, as a pod can be running long before the app inside it is"""
        last_error = "no answer yet"
        while time.monotonic() < deadline:
            try:
                with urllib.request.urlopen(self.url + path, timeout=10) as response:
                    if response.status < 300:
                        return
                    last_error = f"status {response.status}"
            except urllib.error.HTTPError as error:
                # qBittorrent answers 403 before a login, which still means it's up
                if error.code in (401, 403):
                    return
                last_error = f"status {error.code}"
            except (urllib.error.URLError, OSError) as error:
                last_error = str(error)
            time.sleep(5)

        raise SetupError(f"{self.name} wasn't ready after {READY_TIMEOUT} seconds: {last_error}")


def log(message):
    print(message, flush=True)


def servarr(name, variable, api_version):
    url = os.environ.get(f"{variable}_URL", "")
    if not url:
        return None

    app = App(name, url, os.environ.get(f"{variable}_API_KEY", ""))
    app.headers["X-Api-Key"] = app.api_key
    app.api = f"/api/{api_version}"

    return app


def configure_servarr_login(app):
    """Replaces the 'create a login' prompt the app shows on its first visit with the bbe admin account"""
    host = app.get(f"{app.api}/config/host")
    host.update({
        "authenticationMethod": "forms",
        "authenticationRequired": "enabled",
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD,
        "passwordConfirmation": ADMIN_PASSWORD,
    })
    app.put(f"{app.api}/config/host/{host['id']}", host)
    log(f"{app.name}: login set up for `{ADMIN_USERNAME}`")


def upsert_provider(app, resource, implementation, name, fields, extra=None):
    """Adds a download client or application from the app's own schema, or updates the one bbe added before.

    Later runs find bbe's connection again by its name, which is why each one needs its own.
    """
    existing = next((item for item in app.get(f"{app.api}/{resource}") if item["name"] == name), None)
    if existing is None:
        schemas = app.get(f"{app.api}/{resource}/schema")
        item = next((schema for schema in schemas if schema["implementation"] == implementation), None)
        if item is None:
            raise SetupError(f"{app.name} doesn't support {implementation}")
        item.update({"name": name, "enable": True})
    else:
        item = existing
    item.update(extra or {})

    known = {field["name"] for field in item["fields"]}
    missing = sorted(set(fields) - known)
    if missing:
        raise SetupError(f"{app.name}'s {implementation} settings have no {', '.join(missing)}")
    for field in item["fields"]:
        if field["name"] in fields:
            field["value"] = fields[field["name"]]

    # Saving tests the connection, so a wrong address or key fails here rather than later
    if existing is None:
        app.post(f"{app.api}/{resource}", item)
        log(f"{app.name}: added {name}")
    else:
        app.put(f"{app.api}/{resource}/{existing['id']}", item)
        log(f"{app.name}: updated {name}")


def ensure_root_folder(app, path):
    if any(folder["path"].rstrip("/") == path for folder in app.get(f"{app.api}/rootfolder")):
        return

    app.post(f"{app.api}/rootfolder", {"path": path})
    log(f"{app.name}: added root folder {path}")


def configure_qbittorrent(qbittorrent):
    """The login itself is set by the qBittorrent chart before it starts, from the same secret"""
    result = qbittorrent.request(
        "POST", "/api/v2/auth/login",
        form={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
        headers={"Referer": qbittorrent.url},
    )
    # qBittorrent 5 answers 204 with no body, older versions "Ok." and "Fails." both with 200
    if result not in (None, "Ok."):
        raise SetupError(f"qBittorrent refused the login for `{ADMIN_USERNAME}`: {result}")

    # Downloads go on the shared library, so Sonarr and Radarr can move them without copying
    qbittorrent.post("/api/v2/app/setPreferences", form={"json": json.dumps({"save_path": DOWNLOADS_DIR})})
    log(f"qBittorrent: downloads saved to {DOWNLOADS_DIR}")


def configure_arr(app, qbittorrent, root_folder, category_field, category):
    configure_servarr_login(app)
    ensure_root_folder(app, root_folder)
    if qbittorrent is not None:
        upsert_provider(app, "downloadclient", "QBittorrent", "qBittorrent", {
            "host": qbittorrent.host,
            "port": qbittorrent.port,
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD,
            category_field: category,
        })


def configure_prowlarr(prowlarr, apps):
    """Prowlarr pushes the indexers added to it into every app connected here"""
    configure_servarr_login(prowlarr)
    for app in apps:
        upsert_provider(prowlarr, "applications", app.name, app.name, {
            "prowlarrUrl": prowlarr.url,
            "baseUrl": app.url,
            "apiKey": app.api_key,
        }, extra={"syncLevel": "fullSync"})


def configure_bazarr(bazarr, apps):
    form = {
        "settings-auth-type": "form",
        "settings-auth-username": ADMIN_USERNAME,
        # Bazarr stores a hash of the password it's given
        "settings-auth-password": ADMIN_PASSWORD,
    }
    for app in apps:
        key = app.name.lower()
        form.update({
            f"settings-general-use_{key}": "true",
            f"settings-{key}-ip": app.host,
            f"settings-{key}-port": str(app.port),
            f"settings-{key}-base_url": "/",
            f"settings-{key}-ssl": "false",
            f"settings-{key}-apikey": app.api_key,
        })

    bazarr.post("/api/system/settings", form=form)
    log(f"Bazarr: login set up and connected to {', '.join(app.name for app in apps)}")


def configure_jellyfin(jellyfin):
    """Completes the startup wizard with the bbe admin account and adds the TV and movie libraries"""
    info = jellyfin.get("/System/Info/Public")
    if not info.get("StartupWizardCompleted"):
        jellyfin.post("/Startup/Configuration", {"UICulture": "en-US", "MetadataCountryCode": "US", "PreferredMetadataLanguage": "en"})
        jellyfin.get("/Startup/User")
        jellyfin.post("/Startup/User", {"Name": ADMIN_USERNAME, "Password": ADMIN_PASSWORD})
        jellyfin.post("/Startup/RemoteAccess", {"EnableRemoteAccess": True, "EnableAutomaticPortMapping": False})
        jellyfin.post("/Startup/Complete")
        log(f"Jellyfin: startup wizard completed with `{ADMIN_USERNAME}`")

    session = jellyfin.post("/Users/AuthenticateByName", {"Username": ADMIN_USERNAME, "Pw": ADMIN_PASSWORD}, headers={"Authorization": JELLYFIN_CLIENT})
    jellyfin.headers["Authorization"] = f'{JELLYFIN_CLIENT}, Token="{session["AccessToken"]}"'

    folders = jellyfin.get("/Library/VirtualFolders")
    for name, collection, path in (("Shows", "tvshows", TV_DIR), ("Movies", "movies", MOVIES_DIR)):
        if any(path in (location.rstrip("/") for location in folder.get("Locations", [])) for folder in folders):
            continue

        query = urllib.parse.urlencode({"name": name, "collectionType": collection, "refreshLibrary": "true"})
        jellyfin.post(f"/Library/VirtualFolders?{query}", {"LibraryOptions": {"PathInfos": [{"Path": path}]}})
        log(f"Jellyfin: added the {name} library for {path}")


def configure_jellyseerr(jellyseerr, jellyfin, sonarr, radarr):
    """Signs in with the Jellyfin admin account, which makes it Jellyseerr's admin, then connects Sonarr and Radarr"""
    public = jellyseerr.get("/api/v1/settings/public")
    login = {"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD, "email": f"{ADMIN_USERNAME}@bbe.local"}
    # 4 means no media server is set up yet, and Jellyseerr only accepts the Jellyfin address then
    if public.get("mediaServerType") == 4:
        login.update({"hostname": jellyfin.host, "port": jellyfin.port, "useSsl": False, "urlBase": "", "serverType": 2})
    jellyseerr.post("/api/v1/auth/jellyfin", login)

    if not public.get("initialized"):
        libraries = jellyseerr.get("/api/v1/settings/jellyfin/library?sync=true")
        enabled = ",".join(library["id"] for library in libraries)
        jellyseerr.get(f"/api/v1/settings/jellyfin/library?{urllib.parse.urlencode({'enable': enabled})}")
        log(f"Jellyseerr: signed in to Jellyfin and enabled {len(libraries)} libraries")

    for app, root_folder, extra in (
        (sonarr, TV_DIR, {"seriesType": "standard", "animeSeriesType": "anime", "enableSeasonFolders": True}),
        (radarr, MOVIES_DIR, {"minimumAvailability": "released"}),
    ):
        if app is not None:
            configure_jellyseerr_server(jellyseerr, app, root_folder, extra)

    if not public.get("initialized"):
        jellyseerr.post("/api/v1/settings/initialize")
        log("Jellyseerr: setup completed")


def configure_jellyseerr_server(jellyseerr, app, root_folder, extra):
    resource = f"/api/v1/settings/{app.name.lower()}"
    connection = {"hostname": app.host, "port": app.port, "apiKey": app.api_key, "useSsl": False, "baseUrl": ""}
    existing = next((server for server in jellyseerr.get(resource) if server["hostname"] == app.host), None)

    # Testing the connection also lists the quality profiles to pick from
    profiles = jellyseerr.post(f"{resource}/test", connection)["profiles"]
    profile = next((profile for profile in profiles if profile["name"] == "HD-1080p"), profiles[0])

    server = {
        **(existing or {}),
        **connection,
        "name": app.name,
        "activeProfileId": profile["id"],
        "activeProfileName": profile["name"],
        "activeDirectory": root_folder,
        "is4k": False,
        "isDefault": True,
        "syncEnabled": True,
        "preventSearch": False,
        "tagRequests": False,
        "tags": [],
        **extra,
    }
    if existing is None:
        jellyseerr.post(resource, server)
        log(f"Jellyseerr: connected to {app.name}")
    else:
        # Keep the profile and folder someone picked in Jellyseerr, only the connection is bbe's
        server.update({key: existing[key] for key in ("activeProfileId", "activeProfileName", "activeDirectory") if key in existing})
        jellyseerr.put(f"{resource}/{existing['id']}", server)
        log(f"Jellyseerr: updated the connection to {app.name}")


def main():
    if not ADMIN_USERNAME or not ADMIN_PASSWORD:
        raise SetupError("ADMIN_USERNAME and ADMIN_PASSWORD are required")

    sonarr = servarr("Sonarr", "SONARR", "v3")
    radarr = servarr("Radarr", "RADARR", "v3")
    prowlarr = servarr("Prowlarr", "PROWLARR", "v1")
    bazarr = App("Bazarr", os.environ["BAZARR_URL"], os.environ.get("BAZARR_API_KEY", ""), {"X-API-KEY": os.environ.get("BAZARR_API_KEY", "")}) if os.environ.get("BAZARR_URL") else None
    qbittorrent = App("qBittorrent", os.environ["QBITTORRENT_URL"]) if os.environ.get("QBITTORRENT_URL") else None
    jellyfin = App("Jellyfin", os.environ["JELLYFIN_URL"]) if os.environ.get("JELLYFIN_URL") else None
    jellyseerr = App("Jellyseerr", os.environ["JELLYSEERR_URL"]) if os.environ.get("JELLYSEERR_URL") else None
    arrs = [app for app in (sonarr, radarr) if app is not None]

    deadline = time.monotonic() + READY_TIMEOUT
    readiness = [(sonarr, "/ping"), (radarr, "/ping"), (prowlarr, "/ping"), (bazarr, "/"), (qbittorrent, "/api/v2/app/version"), (jellyfin, "/health"), (jellyseerr, "/api/v1/status")]
    for app, path in readiness:
        if app is not None:
            app.wait_until_ready(path, deadline)
            log(f"{app.name}: ready")

    for path in (TV_DIR, MOVIES_DIR, DOWNLOADS_DIR):
        os.makedirs(path, exist_ok=True)

    # Each app is set up on its own, so one failing still lets the others finish before the job retries
    steps = []
    if qbittorrent:
        steps.append(("qBittorrent", configure_qbittorrent, qbittorrent))
    if sonarr:
        steps.append(("Sonarr", configure_arr, sonarr, qbittorrent, TV_DIR, "tvCategory", "tv-sonarr"))
    if radarr:
        steps.append(("Radarr", configure_arr, radarr, qbittorrent, MOVIES_DIR, "movieCategory", "radarr"))
    if prowlarr:
        steps.append(("Prowlarr", configure_prowlarr, prowlarr, arrs))
    if bazarr and arrs:
        steps.append(("Bazarr", configure_bazarr, bazarr, arrs))
    if jellyfin:
        steps.append(("Jellyfin", configure_jellyfin, jellyfin))
    if jellyseerr and jellyfin:
        steps.append(("Jellyseerr", configure_jellyseerr, jellyseerr, jellyfin, sonarr, radarr))

    failed = []
    for name, step, *arguments in steps:
        try:
            step(*arguments)
        except SetupError as error:
            log(f"ERROR {error}")
            failed.append(name)

    if failed:
        raise SetupError(f"Setting up {', '.join(failed)} failed, the job will try again")

    log("All apps are connected")


if __name__ == "__main__":
    try:
        main()
    except SetupError as error:
        log(f"ERROR {error}")
        sys.exit(1)
