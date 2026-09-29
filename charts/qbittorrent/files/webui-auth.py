"""Sets the qBittorrent WebUI login from a Kubernetes secret before qBittorrent starts.

Without it, qBittorrent 4.6.1 and later only print a temporary password to the log on every start.
The password is written the way qBittorrent stores it itself: PBKDF2-HMAC-SHA512 with 100000
iterations and a 16 byte salt, as `@ByteArray(<salt>:<hash>)` in base64. A hash that already
matches the password is kept, so restarts don't rewrite the file.
"""

import base64
import hashlib
import hmac
import os
import re
import shutil

CONFIG_FILE = os.environ.get("QBITTORRENT_CONFIG", "/config/qBittorrent/qBittorrent.conf")
DEFAULT_CONFIG_FILE = os.environ.get("QBITTORRENT_DEFAULT_CONFIG", "/defaults/qBittorrent.conf")
ITERATIONS = 100000


def hash_password(password, salt=None):
    salt = salt or os.urandom(16)
    key = hashlib.pbkdf2_hmac("sha512", password.encode(), salt, ITERATIONS)
    return f"@ByteArray({base64.b64encode(salt).decode()}:{base64.b64encode(key).decode()})"


def matches(stored, password):
    found = re.fullmatch(r'"?@ByteArray\(([^:]+):([^)]+)\)"?', stored or "")
    if not found:
        return False

    salt = base64.b64decode(found.group(1))
    return hmac.compare_digest(hash_password(password, salt), f"@ByteArray({found.group(1)}:{found.group(2)})")


def set_preferences(lines, values):
    """Sets keys in the [Preferences] section, adding the section when it's missing"""
    start = next((i for i, line in enumerate(lines) if line.strip() == "[Preferences]"), None)
    if start is None:
        lines += ["", "[Preferences]"]
        start = len(lines) - 1

    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("[")), len(lines))
    for key, value in values.items():
        index = next((i for i in range(start + 1, end) if lines[i].split("=", 1)[0] == key), None)
        if index is None:
            lines.insert(end, f"{key}={value}")
            end += 1
        else:
            lines[index] = f"{key}={value}"

    return lines


def read_preference(lines, key):
    for line in lines:
        name, _, value = line.partition("=")
        if name == key:
            return value

    return None


def main():
    username = os.environ["WEBUI_USERNAME"]
    password = os.environ["WEBUI_PASSWORD"]

    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    # Start from the image's defaults like its own start script would, as it skips them once the file exists
    if not os.path.exists(CONFIG_FILE) and os.path.exists(DEFAULT_CONFIG_FILE):
        shutil.copyfile(DEFAULT_CONFIG_FILE, CONFIG_FILE)

    lines = []
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as file:
            lines = file.read().splitlines()

    stored = read_preference(lines, "WebUI\\Password_PBKDF2")
    values = {"WebUI\\Username": username}
    if not matches(stored, password):
        values["WebUI\\Password_PBKDF2"] = f'"{hash_password(password)}"'

    with open(CONFIG_FILE, "w") as file:
        file.write("\n".join(set_preferences(lines, values)) + "\n")

    print(f"qBittorrent WebUI login set for `{username}`", flush=True)


if __name__ == "__main__":
    main()
