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
# Where Jellyfin transcodes, a bounded volume on the node, or empty to keep Jellyfin's own default
TRANSCODE_DIR = os.environ.get("JELLYFIN_TRANSCODE_DIR", "")
# Where qBittorrent keeps downloads in progress, a volume on the node, or empty to keep them in DOWNLOADS_DIR
INCOMPLETE_DIR = os.environ.get("QBITTORRENT_INCOMPLETE_DIR", "")
READY_TIMEOUT = int(os.environ.get("READY_TIMEOUT", "900"))
# The indexers bbe adds to Prowlarr, from `bbe configure`, with their credentials as files in INDEXER_SECRETS_DIR
INDEXERS = json.loads(os.environ.get("INDEXERS") or "[]")
INDEXER_SECRETS_DIR = os.environ.get("INDEXER_SECRETS_DIR", "/indexer-secrets")
# Marks the indexers bbe added, so it only ever changes or removes its own
BBE_TAG = "bbe"
# Prowlarr searches an indexer before saving it, waiting up to 100 seconds, then Sonarr and Radarr test it too
INDEXER_SAVE_TIMEOUT = 300
# FlareSolverr gets past Cloudflare's challenges, for the indexers tagged for it
FLARESOLVERR_URL = os.environ.get("FLARESOLVERR_URL", "")
FLARESOLVERR_TIMEOUT = int(os.environ.get("FLARESOLVERR_TIMEOUT", "60"))
FLARESOLVERR_TAG = "flaresolverr"

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

    def request(self, method, path, body=None, form=None, headers=None, timeout=60):
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
            with self.opener.open(request, timeout=timeout) as response:
                status, content = response.status, response.read()
        except urllib.error.HTTPError as error:
            status, content = error.code, error.read()
        except (urllib.error.URLError, TimeoutError) as error:
            raise SetupError(f"{self.name}: {method} {path} failed: {error}")

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
        item = json.loads(json.dumps(existing))
    item.update(extra or {})

    known = {field["name"] for field in item["fields"]}
    missing = sorted(set(fields) - known)
    if missing:
        raise SetupError(f"{app.name}'s {implementation} settings have no {', '.join(missing)}")
    for field in item["fields"]:
        if field["name"] in fields:
            field["value"] = fields[field["name"]]

    # Saving tests the connection, so a wrong address or key fails here rather than later. An unchanged one isn't
    # saved again, as that would test it on every run
    if existing is None:
        app.post(f"{app.api}/{resource}", item)
        log(f"{app.name}: added {name}")
    elif changed(item, existing):
        app.put(f"{app.api}/{resource}/{existing['id']}", item)
        log(f"{app.name}: updated {name}")


# How the Servarr apps read back a credential
MASKED = "********"


def changed(item, existing):
    """Whether saving would change anything. Credentials read back masked, so they count as unchanged: bbe's come
    from the chart's secrets, which are kept across upgrades"""
    masked = {field["name"] for field in existing.get("fields", []) if field.get("value") == MASKED}
    comparable = json.loads(json.dumps(item))
    for field in comparable.get("fields", []):
        if field["name"] in masked:
            field["value"] = MASKED
    return comparable != existing


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

    # Downloads go on the shared library, so Sonarr and Radarr can move them without copying. While in progress
    # they can stay on the node, which qBittorrent moves them off once complete
    preferences = {"save_path": DOWNLOADS_DIR, "temp_path_enabled": bool(INCOMPLETE_DIR)}
    if INCOMPLETE_DIR:
        preferences["temp_path"] = INCOMPLETE_DIR
    qbittorrent.post("/api/v2/app/setPreferences", form={"json": json.dumps(preferences)})
    if INCOMPLETE_DIR:
        log(f"qBittorrent: downloads kept in {INCOMPLETE_DIR} while in progress, then saved to {DOWNLOADS_DIR}")
    else:
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


def prowlarr_tag(prowlarr, label, create=True):
    """Prowlarr's tag with this label, added when it's missing, or None when it's missing and not created"""
    tag = next((tag for tag in prowlarr.get("/api/v1/tag") if tag["label"] == label), None)
    if tag is None and create:
        tag = prowlarr.post("/api/v1/tag", {"label": label})
    return tag


def configure_prowlarr_flaresolverr(prowlarr):
    """Adds FlareSolverr as Prowlarr's proxy for the indexers tagged for it, as TRaSH's guide sets it up"""
    tag = prowlarr_tag(prowlarr, FLARESOLVERR_TAG)
    upsert_provider(prowlarr, "indexerproxy", "FlareSolverr", "FlareSolverr", {
        "host": FLARESOLVERR_URL,
        "requestTimeout": FLARESOLVERR_TIMEOUT,
    }, extra={"tags": [tag["id"]]})


def configure_prowlarr_indexers(prowlarr, apps):
    """Brings the indexers bbe added in line with the list, leaving the ones added in Prowlarr itself alone"""
    tag = prowlarr_tag(prowlarr, BBE_TAG, create=bool(INDEXERS))
    if tag is None:
        return

    existing = prowlarr.get("/api/v1/indexer")
    wanted = {indexer["name"] for indexer in INDEXERS}
    for indexer in existing:
        if tag["id"] in indexer.get("tags", []) and indexer["name"] not in wanted:
            prowlarr.request("DELETE", f"/api/v1/indexer/{indexer['id']}")
            log(f"Prowlarr: removed the indexer `{indexer['name']}`")
    if not INDEXERS:
        return

    definitions = {definition["definitionName"]: definition for definition in prowlarr.get("/api/v1/indexer/schema")}
    profile_id = prowlarr.get("/api/v1/appprofile")[0]["id"]
    flaresolverr_tag = prowlarr_tag(prowlarr, FLARESOLVERR_TAG, create=False) if FLARESOLVERR_URL else None
    failed = []
    for wanted_indexer in INDEXERS:
        try:
            save_indexer(prowlarr, wanted_indexer, existing, definitions, profile_id, tag, flaresolverr_tag)
        except SetupError as error:
            log(f"ERROR {error}")
            failed.append(wanted_indexer["name"])

    sync_app_indexers(prowlarr, tag, apps)

    # The others are set up, and the job tries these again
    if failed:
        raise SetupError(f"Prowlarr couldn't save the indexers {', '.join(failed)}")


def sync_app_indexers(prowlarr, tag, apps):
    """Makes sure bbe's indexers reach Sonarr and Radarr, and says which haven't.

    Prowlarr syncs an indexer to an app that has no tags, or one sharing a tag with it, so an app someone tagged gets
    bbe's tag too. Then the sync runs now rather than on Prowlarr's schedule. An app still refuses an indexer that
    fails its test, such as one Cloudflare blocks or one Prowlarr disabled after failures, so that's reported.
    """
    for application in prowlarr.get(f"{prowlarr.api}/applications"):
        if application["tags"] and tag["id"] not in application["tags"]:
            application["tags"] = sorted(set(application["tags"]) | {tag["id"]})
            prowlarr.put(f"{prowlarr.api}/applications/{application['id']}", application)
            log(f"Prowlarr: tagged {application['name']} `{BBE_TAG}`, so bbe's indexers sync to it")

    command = prowlarr.post(f"{prowlarr.api}/command", {"name": "ApplicationIndexerSync", "forceSync": True})
    deadline = time.monotonic() + INDEXER_SAVE_TIMEOUT
    while command.get("status") not in ("completed", "failed", "aborted", "cancelled") and time.monotonic() < deadline:
        time.sleep(5)
        command = prowlarr.get(f"{prowlarr.api}/command/{command['id']}")

    for app in apps:
        # Prowlarr names the indexers it syncs after its own, followed by " (Prowlarr)"
        synced = {indexer["name"] for indexer in app.get(f"{app.api}/indexer")}
        missing = [indexer["name"] for indexer in INDEXERS if f"{indexer['name']} (Prowlarr)" not in synced]
        if missing:
            log(f"WARNING {app.name} doesn't have {', '.join(f'`{name}`' for name in missing)} yet, as it refuses an indexer"
                " that fails its test, such as one Cloudflare blocks. Prowlarr's System > Events says why, and it syncs"
                " again every few hours")
        else:
            log(f"{app.name}: has bbe's {len(INDEXERS)} indexers from Prowlarr")


def save_indexer(prowlarr, wanted_indexer, existing, definitions, profile_id, tag, flaresolverr_tag=None):
    """Adds or updates one indexer, and only if bbe added it"""
    name, definition_name = wanted_indexer["name"], wanted_indexer["definition"]
    current = next((indexer for indexer in existing if indexer["name"] == name), None)
    if current is not None and tag["id"] not in current.get("tags", []):
        log(f"Prowlarr: left `{name}` as it is, as it was added in Prowlarr")
        return
    if definition_name not in definitions:
        raise SetupError(f"Prowlarr has no indexer definition `{definition_name}` for `{name}`")

    values = dict(wanted_indexer.get("fields") or {})
    for field, key in (wanted_indexer.get("secretFields") or {}).items():
        try:
            with open(os.path.join(INDEXER_SECRETS_DIR, key)) as secret:
                values[field] = secret.read()
        except OSError:
            raise SetupError(f"The credential `{key}` for `{name}` is missing from the bbe-media-indexers secret, add the indexer again with `bbe configure bbe-media`")

    indexer = json.loads(json.dumps(current if current is not None else definitions[definition_name]))
    unknown = set(values) - {field["name"] for field in indexer["fields"]}
    if unknown:
        raise SetupError(f"Prowlarr's `{definition_name}` definition has no field {', '.join(sorted(unknown))} for `{name}`")
    for field in indexer["fields"]:
        if field["name"] in values:
            field["value"] = values[field["name"]]
    # Every indexer bbe adds is tagged for FlareSolverr, which Prowlarr only sends a request through once Cloudflare
    # challenges it. Cloudflare challenges some indexers now and then, so it can't be told in advance which need it
    tags = set(indexer.get("tags", [])) | {tag["id"]}
    if flaresolverr_tag is not None:
        tags.add(flaresolverr_tag["id"])
    indexer.update({"name": name, "enable": True, "tags": sorted(tags)})
    if not indexer.get("appProfileId"):
        indexer["appProfileId"] = profile_id

    # Prowlarr searches the indexer before saving it, and forceSave only lets a save through warnings
    if current is None:
        prowlarr.post("/api/v1/indexer?forceSave=true", indexer, timeout=INDEXER_SAVE_TIMEOUT)
        log(f"Prowlarr: added the indexer `{name}`")
    elif indexer != current:
        prowlarr.put(f"/api/v1/indexer/{current['id']}?forceSave=true", indexer, timeout=INDEXER_SAVE_TIMEOUT)
        log(f"Prowlarr: updated the indexer `{name}`")


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

    if TRANSCODE_DIR:
        encoding = jellyfin.get("/System/Configuration/encoding")
        if encoding.get("TranscodingTempPath") != TRANSCODE_DIR:
            encoding["TranscodingTempPath"] = TRANSCODE_DIR
            jellyfin.post("/System/Configuration/encoding", encoding)
            log(f"Jellyfin: transcoding in {TRANSCODE_DIR}")


def configure_seerr(seerr, jellyfin, sonarr, radarr):
    """Signs in with the Jellyfin admin account, which makes it Seerr's admin, then connects Sonarr and Radarr"""
    public = seerr.get("/api/v1/settings/public")
    login = {"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD, "email": f"{ADMIN_USERNAME}@bbe.local"}
    # 4 means no media server is set up yet, and Seerr only accepts the Jellyfin address then
    if public.get("mediaServerType") == 4:
        login.update({"hostname": jellyfin.host, "port": jellyfin.port, "useSsl": False, "urlBase": "", "serverType": 2})
    seerr.post("/api/v1/auth/jellyfin", login)

    if not public.get("initialized"):
        # Syncing reads the libraries from Jellyfin, which are then enabled one by one
        libraries = seerr.post("/api/v1/settings/jellyfin/library/sync")
        for library in libraries:
            if not library.get("enabled"):
                seerr.put(f"/api/v1/settings/jellyfin/library/{library['id']}", {"enabled": True})
        log(f"Seerr: signed in to Jellyfin and enabled {len(libraries)} libraries")

    for app, root_folder, extra in (
        (sonarr, TV_DIR, {"seriesType": "standard", "animeSeriesType": "anime", "enableSeasonFolders": True}),
        (radarr, MOVIES_DIR, {"minimumAvailability": "released"}),
    ):
        if app is not None:
            configure_seerr_server(seerr, app, root_folder, extra)

    if not public.get("initialized"):
        seerr.post("/api/v1/settings/initialize")
        log("Seerr: setup completed")


def configure_seerr_server(seerr, app, root_folder, extra):
    resource = f"/api/v1/settings/{app.name.lower()}"
    connection = {"hostname": app.host, "port": app.port, "apiKey": app.api_key, "useSsl": False, "baseUrl": ""}
    existing = next((server for server in seerr.get(resource) if server["hostname"] == app.host), None)

    # Testing the connection also lists the quality profiles to pick from
    profiles = seerr.post(f"{resource}/test", connection)["profiles"]
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
        seerr.post(resource, server)
        log(f"Seerr: connected to {app.name}")
    else:
        # Keep the profile and folder someone picked in Seerr, only the connection is bbe's
        server.update({key: existing[key] for key in ("activeProfileId", "activeProfileName", "activeDirectory") if key in existing})
        # The id is in the path, and Seerr refuses it in the body as it's read-only
        server.pop("id", None)
        if server != {key: value for key, value in existing.items() if key != "id"}:
            seerr.put(f"{resource}/{existing['id']}", server)
            log(f"Seerr: updated the connection to {app.name}")


def main():
    if not ADMIN_USERNAME or not ADMIN_PASSWORD:
        raise SetupError("ADMIN_USERNAME and ADMIN_PASSWORD are required")

    sonarr = servarr("Sonarr", "SONARR", "v3")
    radarr = servarr("Radarr", "RADARR", "v3")
    prowlarr = servarr("Prowlarr", "PROWLARR", "v1")
    bazarr = App("Bazarr", os.environ["BAZARR_URL"], os.environ.get("BAZARR_API_KEY", ""), {"X-API-KEY": os.environ.get("BAZARR_API_KEY", "")}) if os.environ.get("BAZARR_URL") else None
    qbittorrent = App("qBittorrent", os.environ["QBITTORRENT_URL"]) if os.environ.get("QBITTORRENT_URL") else None
    jellyfin = App("Jellyfin", os.environ["JELLYFIN_URL"]) if os.environ.get("JELLYFIN_URL") else None
    seerr = App("Seerr", os.environ["SEERR_URL"]) if os.environ.get("SEERR_URL") else None
    flaresolverr = App("FlareSolverr", FLARESOLVERR_URL) if FLARESOLVERR_URL else None
    arrs = [app for app in (sonarr, radarr) if app is not None]

    deadline = time.monotonic() + READY_TIMEOUT
    # Jellyfin 12 answers /health from its startup screen while the server is still loading, and 503 elsewhere until
    # it's done
    readiness = [(sonarr, "/ping"), (radarr, "/ping"), (prowlarr, "/ping"), (bazarr, "/"), (qbittorrent, "/api/v2/app/version"), (jellyfin, "/System/Info/Public"), (seerr, "/api/v1/status"), (flaresolverr, "/health")]
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
        if flaresolverr:
            steps.append(("FlareSolverr", configure_prowlarr_flaresolverr, prowlarr))
        steps.append(("Prowlarr indexers", configure_prowlarr_indexers, prowlarr, arrs))
    if bazarr and arrs:
        steps.append(("Bazarr", configure_bazarr, bazarr, arrs))
    if jellyfin:
        steps.append(("Jellyfin", configure_jellyfin, jellyfin))
    if seerr and jellyfin:
        steps.append(("Seerr", configure_seerr, seerr, jellyfin, sonarr, radarr))

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
