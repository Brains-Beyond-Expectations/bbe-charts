"""Connects bbe-music's apps after every install and upgrade.

- Lidarr: its login, the music folder, bbe-media's qBittorrent, and bbe-media's Prowlarr sharing its indexers with it.
- Music Assistant: its admin, its address, and the music folders it plays.
- SoulSync: its API key, slskd, bbe-media's Prowlarr and qBittorrent, and Lidarr as sources, Lidarr's music folder
  to mirror Spotify into with Lidarr's naming and an M3U per playlist, and the Spotify address its login comes back to.

Every step reads what's already there first, so running it again changes nothing. Only the Python standard library
is used, so the job runs on the plain python image.
"""

import base64
import http.cookiejar
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

READY_TIMEOUT = int(os.environ.get("READY_TIMEOUT", "900"))
DOMAIN = os.environ.get("DOMAIN", "")
SSO = os.environ.get("SSO", "true").lower() == "true"
MUSIC_DIR = os.environ.get("MUSIC_DIR", "/media/music")
# The Lidarr root folder SoulSync asks Lidarr to download into, outside the music: it copies the tracks it wants into
# the music and has Lidarr forget the rest, which would otherwise stay there as duplicates
SOULSYNC_LIDARR_DIR = os.environ.get("SOULSYNC_LIDARR_DIR", "/media/downloads/soulsync-lidarr")
SOULSEEK_DOWNLOADS = os.environ.get("SOULSEEK_DOWNLOADS", "/media/downloads/soulseek/complete")
DOWNLOADS_DIR = os.environ.get("DOWNLOADS_DIR", "/media/downloads")

LIDARR_URL = os.environ.get("LIDARR_URL", "")
LIDARR_API_KEY = os.environ.get("LIDARR_API_KEY", "")
LIDARR_QUALITY_PROFILE = os.environ.get("LIDARR_QUALITY_PROFILE", "Any")
LIDARR_METADATA_PROFILE = os.environ.get("LIDARR_METADATA_PROFILE", "Standard")
LIDARR_USERNAME = os.environ.get("LIDARR_USERNAME", "")
LIDARR_PASSWORD = os.environ.get("LIDARR_PASSWORD", "")

PROWLARR_URL = os.environ.get("PROWLARR_URL", "")
PROWLARR_API_KEY = os.environ.get("PROWLARR_API_KEY", "")
QBITTORRENT_URL = os.environ.get("QBITTORRENT_URL", "")
QBITTORRENT_USERNAME = os.environ.get("QBITTORRENT_USERNAME", "")
QBITTORRENT_PASSWORD = os.environ.get("QBITTORRENT_PASSWORD", "")
# The ratio torrents seed to, as bbe-media has qBittorrent stop and remove them at
SEED_RATIO = float(os.environ.get("SEED_RATIO") or 0)

MUSIC_ASSISTANT_URL = os.environ.get("MUSIC_ASSISTANT_URL", "")
MUSIC_ASSISTANT_USERNAME = os.environ.get("MUSIC_ASSISTANT_USERNAME", "")
MUSIC_ASSISTANT_PASSWORD = os.environ.get("MUSIC_ASSISTANT_PASSWORD", "")

SOULSYNC_URL = os.environ.get("SOULSYNC_URL", "")
SOULSYNC_KEY_SECRET = os.environ.get("SOULSYNC_KEY_SECRET", "bbe-music-soulsync-key")
SLSKD_URL = os.environ.get("SLSKD_URL", "")
SLSKD_API_KEY = os.environ.get("SLSKD_API_KEY", "")

LIDARR_CLIENT = "qBittorrent (bbe-media)"
LIDARR_CATEGORY = "music"
PROWLARR_APPLICATION = "Lidarr (bbe-music)"
# How the Servarr apps read back a credential
MASKED = "********"


class SetupError(Exception):
    pass


def log(message):
    print(message, flush=True)


class App:
    """One app's HTTP API, keeping the session cookies the apps that log in rely on"""

    def __init__(self, name, url, headers=None):
        self.name = name
        self.url = url.rstrip("/")
        self.headers = headers or {}
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))

    def request(self, method, path, body=None, headers=None, timeout=120):
        request_headers = {"Accept": "application/json", **self.headers, **(headers or {})}
        data = None
        if body is not None:
            data = json.dumps(body).encode()
            request_headers["Content-Type"] = "application/json"

        request = urllib.request.Request(self.url + path, data=data, method=method, headers=request_headers)
        try:
            with self.opener.open(request, timeout=timeout) as response:
                status, content = response.status, response.read()
        except urllib.error.HTTPError as error:
            status, content = error.code, error.read()
        except (urllib.error.URLError, OSError) as error:
            raise SetupError(f"{self.name}: {method} {path} failed: {error}")

        if status >= 300:
            raise SetupError(f"{self.name}: {method} {path} returned {status}: {content[:500].decode(errors='replace')}")
        if not content:
            return None
        try:
            return json.loads(content)
        except ValueError:
            return content.decode(errors="replace")

    def get(self, path):
        return self.request("GET", path)

    def post(self, path, body=None):
        return self.request("POST", path, {} if body is None else body)

    def put(self, path, body):
        return self.request("PUT", path, body)

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
                # Answering at all means it's up
                if error.code in (401, 403, 503):
                    return
                last_error = f"status {error.code}"
            except (urllib.error.URLError, OSError) as error:
                last_error = str(error)
            time.sleep(5)
        raise SetupError(f"{self.name} wasn't ready after {READY_TIMEOUT} seconds: {last_error}")


# ---- Lidarr and Prowlarr ----------------------------------------------------------------------------------------------


def servarr(name, url, api_key):
    app = App(name, url, {"X-Api-Key": api_key})
    app.api = "/api/v1"
    app.api_key = api_key
    return app


def changed(item, existing):
    """Whether saving would change anything. Credentials read back masked, so they count as unchanged: bbe's come
    from the chart's secrets, which are kept across upgrades"""
    masked = {field["name"] for field in existing.get("fields", []) if field.get("value") == MASKED}
    comparable = json.loads(json.dumps(item))
    for field in comparable.get("fields", []):
        if field["name"] in masked:
            field["value"] = MASKED
    return comparable != existing


def upsert_provider(app, resource, implementation, name, fields, extra=None):
    """Adds a download client or application from the app's own schema, or updates the one bbe added before, found
    again by its name"""
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

    # Saving tests the connection, so a wrong address or key fails here rather than later
    if existing is None:
        app.post(f"{app.api}/{resource}", item)
        log(f"{app.name}: added {name}")
    elif changed(item, existing):
        app.put(f"{app.api}/{resource}/{existing['id']}", item)
        log(f"{app.name}: updated {name}")


def configure_lidarr_login(lidarr):
    """Lidarr trusts authentik's forward auth (`external`), and keeps a login of its own for going back to it"""
    host = lidarr.get(f"{lidarr.api}/config/host")
    wanted = {
        "authenticationMethod": "external" if SSO else "forms",
        "authenticationRequired": "enabled",
        "username": LIDARR_USERNAME,
    }
    if all(host.get(key) == value for key, value in wanted.items()):
        return
    host.update(wanted, password=LIDARR_PASSWORD, passwordConfirmation=LIDARR_PASSWORD)
    lidarr.put(f"{lidarr.api}/config/host/{host['id']}", host)
    log(f"Lidarr: {'signs people in through single sign-on' if SSO else f'login set up for `{LIDARR_USERNAME}`'}")


def profile_id(lidarr, kind, name):
    profiles = lidarr.get(f"{lidarr.api}/{kind}")
    found = next((profile for profile in profiles if profile["name"].lower() == name.lower()), None)
    if found is None:
        raise SetupError(f"Lidarr has no {kind} `{name}`, only {', '.join(p['name'] for p in profiles)}")
    return found["id"]


def configure_lidarr_root_folders(lidarr):
    """The music, which Lidarr adds new artists to, and the folder SoulSync has it download into"""
    existing = {folder["path"].rstrip("/") for folder in lidarr.get(f"{lidarr.api}/rootfolder")}
    for name, path in (("Music", MUSIC_DIR), ("SoulSync", SOULSYNC_LIDARR_DIR)):
        if path not in existing:
            add_lidarr_root_folder(lidarr, name, path)


def add_lidarr_root_folder(lidarr, name, path):
    lidarr.post(f"{lidarr.api}/rootfolder", {
        "name": name,
        "path": path,
        "defaultQualityProfileId": profile_id(lidarr, "qualityprofile", LIDARR_QUALITY_PROFILE),
        "defaultMetadataProfileId": profile_id(lidarr, "metadataprofile", LIDARR_METADATA_PROFILE),
        "defaultMonitorOption": "all",
        "defaultNewItemMonitorOption": "all",
        "defaultTags": [],
    })
    log(f"Lidarr: added the root folder {path}")


def configure_lidarr_download_client(lidarr):
    """bbe-media's qBittorrent, which Lidarr 3.1.0 signs in to as bbe-media's admin"""
    if not QBITTORRENT_URL:
        return
    parts = urllib.parse.urlsplit(QBITTORRENT_URL)
    upsert_provider(lidarr, "downloadclient", "QBittorrent", LIDARR_CLIENT, {
        "host": parts.hostname,
        "port": parts.port,
        "username": QBITTORRENT_USERNAME,
        "password": QBITTORRENT_PASSWORD,
        "musicCategory": LIDARR_CATEGORY,
    })


def configure_prowlarr(prowlarr, lidarr):
    """bbe-media's Prowlarr pushes its indexers into Lidarr, as it does into Sonarr and Radarr"""
    upsert_provider(prowlarr, "applications", "Lidarr", PROWLARR_APPLICATION, {
        "prowlarrUrl": PROWLARR_URL,
        "baseUrl": LIDARR_URL,
        "apiKey": lidarr.api_key,
    }, extra={"syncLevel": "fullSync"})


# ---- Music Assistant --------------------------------------------------------------------------------------------------


class MusicAssistant(App):
    """Music Assistant's JSON-RPC API, signed in as its admin"""

    def command(self, command, **args):
        return self.request("POST", "/api", {"message_id": command, "command": command, "args": args})

    def sign_in(self):
        """Creates its first admin, or signs in as it. Until an admin exists anyone could create one, so this runs
        before the apps are reachable from anywhere else"""
        try:
            result = self.request("POST", "/setup", {
                "username": MUSIC_ASSISTANT_USERNAME,
                "password": MUSIC_ASSISTANT_PASSWORD,
                "display_name": "bbe",
            })
            log(f"Music Assistant: created its admin {MUSIC_ASSISTANT_USERNAME}")
        except SetupError as error:
            if "already" not in str(error).lower():
                raise
            result = self.command("auth/login", username=MUSIC_ASSISTANT_USERNAME,
                                  password=MUSIC_ASSISTANT_PASSWORD, provider_id="builtin")
        token = (result or {}).get("token") or (result or {}).get("access_token")
        if not token:
            raise SetupError(f"Music Assistant: {MUSIC_ASSISTANT_USERNAME} couldn't sign in: {result}")
        self.headers["Authorization"] = f"Bearer {token}"


def configure_music_assistant_address(music_assistant):
    """The address its apps and players reach it at, through Traefik"""
    wanted = f"https://music.{DOMAIN}"
    current = music_assistant.command("config/core/get_value", domain="webserver", key="base_url")
    if current == wanted:
        return
    music_assistant.command("config/core/save", domain="webserver", values={"base_url": wanted})
    log(f"Music Assistant: its address is {wanted}")


def music_assistant_has_folder(music_assistant, path):
    """Whether a local files provider already plays the folder. The path is looked for anywhere in their settings, as
    their shape differs between versions"""
    configs = music_assistant.command("config/providers", provider_domain="filesystem_local", include_values=True)
    return any(path in json.dumps(config) for config in configs or [])


def configure_music_assistant_folders(music_assistant):
    """A local files provider for the music, which Lidarr and SoulSync both write to, with SoulSync's playlists. Best
    effort: Music Assistant imports in the background, and a provider it didn't take is left to add in its settings"""
    if music_assistant_has_folder(music_assistant, MUSIC_DIR):
        return
    step = music_assistant.command("config/providers/setup", provider_domain="filesystem_local")
    flow_id = (step or {}).get("flow_id")
    if flow_id:
        step = music_assistant.command("config/flows/submit", flow_id=flow_id,
                                       values={"content_type": "music", "path": MUSIC_DIR})
    if str((step or {}).get("type", "")).lower().endswith("finish") and ((step or {}).get("result") or {}).get("instance_id"):
        log(f"Music Assistant: plays the music in {MUSIC_DIR}, importing it in the background")
    else:
        log(f"WARNING Music Assistant: the local files in {MUSIC_DIR} may not have been added, add them in its "
            f"settings if they're missing: {step}")


# ---- SoulSync ---------------------------------------------------------------------------------------------------------


class Kubernetes:
    """The one Secret the setup's ServiceAccount may change, through the cluster's API"""

    ACCOUNT = "/var/run/secrets/kubernetes.io/serviceaccount"

    def __init__(self):
        with open(f"{self.ACCOUNT}/token") as file:
            self.token = file.read().strip()
        with open(f"{self.ACCOUNT}/namespace") as file:
            self.namespace = file.read().strip()
        self.context = ssl.create_default_context(cafile=f"{self.ACCOUNT}/ca.crt")

    def request(self, method, path, body=None, content_type="application/json"):
        headers = {"Authorization": f"Bearer {self.token}", "Accept": "application/json"}
        data = None
        if body is not None:
            data = json.dumps(body).encode()
            headers["Content-Type"] = content_type
        request = urllib.request.Request(f"https://kubernetes.default.svc{path}", data=data, method=method,
                                         headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=30, context=self.context) as response:
                return json.loads(response.read() or b"{}")
        except urllib.error.HTTPError as error:
            raise SetupError(f"Kubernetes: {method} {path} returned {error.code}: {error.read()[:300]}")

    def secret_value(self, name, key):
        secret = self.request("GET", f"/api/v1/namespaces/{self.namespace}/secrets/{name}")
        value = (secret.get("data") or {}).get(key)
        return base64.b64decode(value).decode() if value else ""

    def set_secret_value(self, name, key, value):
        self.request("PATCH", f"/api/v1/namespaces/{self.namespace}/secrets/{name}",
                     {"data": {key: base64.b64encode(value.encode()).decode()}}, "application/merge-patch+json")


def soulsync_key(soulsync, kubernetes):
    """SoulSync makes its own API keys: the first one without a key, which the setup keeps in its Secret"""
    key = kubernetes.secret_value(SOULSYNC_KEY_SECRET, "api-key")
    if key:
        return key
    try:
        result = soulsync.request("POST", "/api/v1/api-keys/bootstrap", {"label": "bbe-music setup"})
    except SetupError as error:
        raise SetupError(f"SoulSync already has API keys, but not the one bbe keeps in {SOULSYNC_KEY_SECRET}. "
                         f"Create an admin key in SoulSync and save it there as `api-key`: {error}")
    data = (result or {}).get("data") or result or {}
    key = data.get("key") or data.get("api_key") or data.get("raw_key")
    if not key:
        raise SetupError(f"SoulSync didn't answer with a key: {list(data)}")
    kubernetes.set_secret_value(SOULSYNC_KEY_SECRET, "api-key", key)
    log("SoulSync: made bbe's API key")
    return key


def soulsync_settings():
    """Standalone, writing files and playlists rather than to a media server. Soulseek first, then torrents"""
    settings = {
        "active_media_server": "soulsync",
        "soulseek": {
            "slskd_url": SLSKD_URL,
            "api_key": SLSKD_API_KEY,
            "download_path": SOULSEEK_DOWNLOADS,
            "transfer_path": MUSIC_DIR,
        },
        "download_source": {"mode": "hybrid", "hybrid_order": ["soulseek"]},
        # Into the music, named as Lidarr names it, so it sees what Lidarr has and nothing is there twice
        "file_organization": {"enabled": True, "templates": {
            "album_path": "$albumartist/$album ($year)/$albumartist - $album - $track - $title",
            "single_path": "$albumartist/$title ($year)/$albumartist - $title",
            "compilation_path": "Various Artists/$album ($year)/$artist - $album - $track - $title",
            "playlist_path": "Playlists/$playlist/$artist - $title",
        }},
        # Each playlist as an M3U next to its tracks, which Music Assistant reads
        "m3u_export": {"enabled": True, "relative_paths": True},
        # Spotify sends its login back here, through authentik
        "spotify": {"redirect_uri": f"https://soulsync.{DOMAIN}/callback"},
        "security": {"trust_reverse_proxy": True},
    }
    order = ["soulseek"]
    if PROWLARR_URL and QBITTORRENT_URL:
        order.append("torrent")
        settings["download_source"]["torrent_download_path"] = DOWNLOADS_DIR
        settings["prowlarr"] = {"url": PROWLARR_URL, "api_key": PROWLARR_API_KEY}
        settings["torrent_client"] = {
            "type": "qbittorrent",
            "url": QBITTORRENT_URL,
            "username": QBITTORRENT_USERNAME,
            "password": QBITTORRENT_PASSWORD,
            # qBittorrent enforces the ratio, as it does for everything else
            "seed_mode": "client",
            "seed_ratio_goal": SEED_RATIO,
            "seed_remove_data": True,
        }
    if LIDARR_URL:
        # Lidarr finds whole albums, of which SoulSync takes the tracks it wants
        order.append("lidarr")
        settings["lidarr_download"] = {
            "url": LIDARR_URL,
            "api_key": LIDARR_API_KEY,
            "root_folder": SOULSYNC_LIDARR_DIR,
            "quality_profile": LIDARR_QUALITY_PROFILE,
            "cleanup_after_import": True,
        }
    settings["download_source"]["hybrid_order"] = order
    return settings


def configure_soulsync(soulsync, kubernetes):
    key = soulsync_key(soulsync, kubernetes)
    soulsync.headers["X-API-Key"] = key
    # Its settings come back with secrets masked, so they're all saved, which is what makes it reload its sources
    soulsync.post("/api/settings", soulsync_settings())
    sources = soulsync_settings()["download_source"]["hybrid_order"]
    log(f"SoulSync: mirrors into {MUSIC_DIR}, from {', '.join(sources)}")


def main():
    deadline = time.monotonic() + READY_TIMEOUT

    if LIDARR_URL:
        lidarr = servarr("Lidarr", LIDARR_URL, LIDARR_API_KEY)
        lidarr.wait_until_ready("/ping", deadline)
        configure_lidarr_login(lidarr)
        configure_lidarr_root_folders(lidarr)
        configure_lidarr_download_client(lidarr)
        if PROWLARR_URL:
            prowlarr = servarr("Prowlarr", PROWLARR_URL, PROWLARR_API_KEY)
            prowlarr.wait_until_ready("/ping", deadline)
            configure_prowlarr(prowlarr, lidarr)
        log("Lidarr: ready")

    if MUSIC_ASSISTANT_URL:
        music_assistant = MusicAssistant("Music Assistant", MUSIC_ASSISTANT_URL)
        music_assistant.wait_until_ready("/", deadline)
        music_assistant.sign_in()
        configure_music_assistant_address(music_assistant)
        configure_music_assistant_folders(music_assistant)
        log("Music Assistant: ready")

    if SOULSYNC_URL:
        soulsync = App("SoulSync", SOULSYNC_URL)
        soulsync.wait_until_ready("/", deadline)
        configure_soulsync(soulsync, Kubernetes())
        log("SoulSync: ready")

    log("The music is set up")


if __name__ == "__main__":
    try:
        main()
    except SetupError as error:
        log(f"ERROR {error}")
        sys.exit(1)
