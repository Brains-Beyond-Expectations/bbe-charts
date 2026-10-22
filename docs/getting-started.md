# Getting started

This guide takes you from a fresh BBE cluster to every app running, with your household signing in to all of them with one account each. It follows the order bbe installs things in, so you can stop after any step and come back later.

## What you'll end up with

| Package | What it gives you | Where |
|---|---|---|
| bbe-storage | Longhorn, storage on the nodes' disks for the apps' databases | |
| bbe-networking | Addresses and HTTPS for every app, a DNS server for the house, and a dashboard listing everything | `https://bbe.home.arpa` |
| bbe-auth | authentik: one account per person for every app | `https://auth.bbe.home.arpa` |
| bbe-media | Jellyfin to watch, Seerr to ask for shows and movies, and Sonarr, Radarr, Prowlarr, Bazarr and qBittorrent to get them | `https://jellyfin.bbe.home.arpa`, … |
| bbe-library | A book library to read and send to e-readers, and Shelfmark to find books | `https://calibre.bbe.home.arpa`, `https://shelfmark.bbe.home.arpa` |
| bbe-music | Music Assistant to play music on the house's speakers, Lidarr to find albums, Soulseek, and SoulSync to keep a copy of your Spotify library | `https://music.bbe.home.arpa`, … |
| bbe-observability | Grafana, with the cluster's metrics and logs, and alerts when something goes wrong | `https://grafana.bbe.home.arpa` |

`bbe.home.arpa` is the default domain. You can choose another one under `home.arpa` when you install bbe-networking.

## Before you start

You'll need:
- **A BBE cluster**, set up with `bbe setup`, as [bbe-quest's README](https://github.com/Brains-Beyond-Expectations/bbe-quest#getting-started) describes. Keep the `~/.bbe` folder it creates: `~/.bbe/bbe.yaml` holds everything bbe installs and its settings, so it's what rebuilds the cluster later.
- **A NAS with NFS** for the media, books and music. The steps below are for Synology.
- **Access to your router's settings**, to keep some addresses free and point devices at the cluster's DNS.
- **Optional:**
  - A **ProtonVPN Plus** account, to send downloads through a VPN.
  - **Spotify Premium**, to play Spotify and keep a local copy of your library.

## 1. Keep two addresses free on your network

The cluster serves its apps and its DNS at addresses of their own on your network, which MetalLB announces:
- one for the **apps** (Traefik), for example `192.168.1.241`;
- one for the **DNS server** (Blocky), for example `192.168.1.240`;
- optionally a third for **Soulseek** without a VPN (step 9).

Pick addresses on the same network as your nodes, **outside your router's DHCP range**, so nothing else gets them. bbe asks for them when it installs bbe-networking.

## 2. Prepare a share on the NAS

The apps write the media, books and music to one NFS share, as a NAS user of their own, never as root:

1. **Create the user:** Control Panel → User & Group → Create, for example `bbe-media`, with a long random password. Keep it out of `administrators`, and deny it every application.
2. **Create the share:** Control Panel → Shared Folder → Create, for example `bbe-media`. Give the user Read/Write, and nobody else access.
3. **Find the user's IDs:** run `id bbe-media` over SSH, or as a one-off Task Scheduler script writing to a file. It prints something like `uid=1031(bbe-media) gid=100(users)`. bbe asks for both numbers.
4. **Allow the nodes:** edit the share → NFS Permissions → Create:
   - Hostname or IP: your nodes' IPs or their range
   - Privilege: Read/Write
   - Squash: **Map root to guest**
   - Security: `sys`
   - Tick **Allow users to access mounted subfolders**
5. **Turn on NFSv4:** Control Panel → File Services → NFS → Maximum NFS protocol: NFSv4, or NFSv4.1 where offered.

Use **the same share and user for every package**. The apps then move files between their folders instead of copying them, and Lidarr and Shelfmark find qBittorrent's downloads.

## 3. Install the packages

Run:

```
bbe install
```

Tick the packages you want. bbe installs what each one needs first, offering to install it, and asks for the values it needs:

| Package | bbe asks for |
|---|---|
| bbe-storage | Nothing. It may offer to prepare the nodes for Longhorn |
| bbe-networking | The apps' address and the DNS server's address from step 1 |
| bbe-auth | The first admin's username (lower case) and email |
| bbe-media | The NFS server and path, the NAS user's IDs, and an admin username for the apps |
| bbe-library | The NFS server and path, and the NAS user's IDs |
| bbe-music | The NFS server and path, and the NAS user's IDs |
| bbe-observability | Nothing |

Each package prints notes when it's installed, with its addresses and how to get its passwords. They're shown again whenever it's upgraded. Each also sets itself up in the background for a few minutes after a first install.

## 4. Make your devices find the apps

### DNS

Blocky answers for `bbe.home.arpa` and everything under it. The easiest way to have every device use it is your router's DHCP settings: set the DNS server it hands out to Blocky's address. Devices pick it up the next time they connect.

To try it on one computer first, add the names to its hosts file, all at the apps' address. Windows only reads the first 9 names on a line, so split them across lines:

```
192.168.1.241  bbe.home.arpa auth.bbe.home.arpa jellyfin.bbe.home.arpa seerr.bbe.home.arpa
192.168.1.241  sonarr.bbe.home.arpa radarr.bbe.home.arpa prowlarr.bbe.home.arpa bazarr.bbe.home.arpa
192.168.1.241  qbittorrent.bbe.home.arpa calibre.bbe.home.arpa shelfmark.bbe.home.arpa music.bbe.home.arpa
192.168.1.241  lidarr.bbe.home.arpa slskd.bbe.home.arpa soulsync.bbe.home.arpa
```

### The certificate

The apps' certificate comes from the cluster's own certificate authority. Browsers and apps warn about it until a device trusts it. Save it with:

```
kubectl get secret bbe-ca -n bbe-networking -o jsonpath='{.data.ca\.crt}' | base64 -d > bbe-ca.crt
```

Then add it to each device's trusted certificates:
- **Windows:** double-click it → Install Certificate → Local Machine → "Trusted Root Certification Authorities".
- **macOS:** open it in Keychain Access, then set it to "Always Trust".
- **iOS:** send it to the phone, install the profile in Settings, then turn it on in General → About → Certificate Trust Settings.
- **Android:** Settings → Security → Encryption & credentials → Install a certificate → CA certificate.
- **Firefox** keeps its own list: Settings → Privacy & Security → Certificates → Import.

Then open `https://bbe.home.arpa`, which lists every app installed.

## 5. Sign in, and add your household

The first admin's password is generated. Get it with:

```
kubectl get secret bbe-auth-admin -n bbe-auth -o jsonpath='{.data.password}' | base64 -d
```

Sign in at `https://auth.bbe.home.arpa`, and change it under your user settings.

People are in one of two groups:
- **`users`** watch, read and listen: Jellyfin, Seerr, the book library, Shelfmark.
- **`admins`** also manage everything: Sonarr, Radarr, Lidarr, qBittorrent and the rest.

Add people in either of two ways:
- **With bbe:** `bbe configure bbe-auth` adds and removes people, and shows each one's first password once.
- **In authentik:** at `https://auth.bbe.home.arpa/if/admin/` → Directory → Users → New User:
  - Type: Internal.
  - Leave the path as `users`.
  - Set a password, then add them to `users` or `admins` on their Groups tab.

Everyone then uses that one username and password everywhere: in the browser, in Jellyfin's TV and phone apps, and on e-readers.

## 6. Media

- **Indexers:** Prowlarr searches the sites you add, and shares them with Sonarr, Radarr and Lidarr. When you install bbe-media, bbe offers a set of public ones. Add or remove them with `bbe configure bbe-media`.
- **Watching:** sign in to `https://jellyfin.bbe.home.arpa`, or Jellyfin's TV and phone apps, with your authentik username and password.
- **Asking for shows and movies:** at `https://seerr.bbe.home.arpa`, with "Use your Jellyfin account".
- **Downloads:** qBittorrent seeds each torrent to a ratio of 2, then removes it. The library keeps its own copy. Change that with `bbe.media.seeding` in `bbe.yaml`.

## 7. Books

- **Reading:** sign in to `https://calibre.bbe.home.arpa` with your authentik account. Within 10 minutes of your first sign-in, books you send to your e-reader go to your account's email address, if it has one.
- **E-readers:**
  - **OPDS apps** (KOReader, Moon+ Reader, …): use `https://calibre.bbe.home.arpa/opds`, with the same username and password.
  - **Kobo devices:** make a sync link under your profile.
- **Finding books:** at `https://shelfmark.bbe.home.arpa`. Downloads land in the library by themselves.

## 8. Music

- **Playing:** at `https://music.bbe.home.arpa`, or with Music Assistant's apps, connecting to `music.bbe.home.arpa` on port 443.
  - It finds the speakers in the house by itself.
  - Its admin is `music-admin`. Get its password with:
    ```
    kubectl get secret bbe-music-admin -n bbe-music -o jsonpath='{.data.password}' | base64 -d
    ```
  - It can't sign in with authentik yet, so add the household in its Settings → Users.
- **Spotify in Music Assistant:** add the Spotify provider in its Settings → Providers, and sign in with your Premium account. Where there's a local copy of a track, it plays that one, also when Spotify is down.
- **Finding albums:** at `https://lidarr.bbe.home.arpa`. It searches your indexers, and Soulseek for what they don't have.
- **A copy of your Spotify library:** SoulSync downloads your liked songs and playlists track by track, and writes each playlist as a file Music Assistant plays. Set it up once:
  1. Create an app at https://developer.spotify.com/dashboard with your Premium account, with the redirect URI `https://soulsync.bbe.home.arpa/callback`.
  2. Put its client ID and secret in SoulSync's Settings → Spotify at `https://soulsync.bbe.home.arpa`, and sign in. Spotify asks again every six months.
  3. Choose the playlists to keep, and your Liked Songs. Spotify only lets SoulSync read playlists you own or collaborate on, so save a copy of other people's playlists as your own first.

## 9. Downloading through a VPN, or not

qBittorrent and Soulseek (slskd) exchange files with people directly. Both work without a VPN, and without opening anything on your router: they then only reach people whose own connection is open, so they find a bit less. There are two ways to reach everyone.

### Option A: through ProtonVPN (recommended)

All of qBittorrent's and slskd's traffic goes through the VPN, and people reach them through a port ProtonVPN forwards. **With the VPN down, nothing gets out.** Nothing is opened at home.

You need ProtonVPN Plus, for its port forwarding.

1. **Make two WireGuard configurations**, one for qBittorrent and one for slskd. At https://account.protonvpn.com → Downloads → WireGuard configuration:
   - Platform: Linux.
   - Turn on **NAT-PMP (Port Forwarding)**.
   - Create. Copy the `PrivateKey` line's value from each.
2. **Give them to the cluster.** They're never written to `bbe.yaml`:
   ```
   kubectl create secret generic bbe-vpn -n bbe-media \
     --from-literal=qbittorrent='<first private key>' \
     --from-literal=slskd='<second private key>'
   ```
3. **Turn it on** in `~/.bbe/bbe.yaml`, under both the `bbe-media` and `bbe-music` packages' values:
   ```yaml
   global:
     bbe:
       vpn:
         enabled: true
         serverCountries: Netherlands   # optional
   ```
4. **Apply it:** run `bbe upgrade`.

To check it's working, read the VPN's log:

```
kubectl logs -n bbe-media deploy/bbe-media-qbittorrent -c gluetun
```

It should show the tunnel connecting and a forwarded port. The namespaces of bbe-media and bbe-music run with the `privileged` pod security level, as the VPN changes their pods' network.

### Option B: directly, with a port forwarded on your router

For Soulseek only. People reach slskd at an address of its own on your network, and your router forwards one port to it:

1. Pick a third free address from step 1, for example `192.168.1.242`.
2. Set it under the `bbe-music` package's values in `~/.bbe/bbe.yaml`:
   ```yaml
   bbe:
     music:
       slskd:
         loadBalancerIP: 192.168.1.242
   ```
3. Run `bbe upgrade`.
4. On your router, forward TCP port **50300** to that address.

This opens one port of your home network to the internet, which only reaches slskd.

## 10. Watching the cluster

bbe-observability keeps the cluster's metrics and the apps' logs for 15 days, and alerts when something goes wrong: a node down, a disk filling up, a Longhorn volume losing its copies, or a certificate not renewing.

- **Looking:** at `https://grafana.bbe.home.arpa`, for admins. Its dashboards show each node, namespace and pod, and the apps' logs are under Explore → Loki.
- **Getting alerts:** they're only shown in Grafana until you say where to send them. For example, to a Telegram chat:
  1. Make a bot with [@BotFather](https://t.me/BotFather), and find your chat's ID.
  2. Give the cluster the bot's token. It's never written to `bbe.yaml`:
     ```
     kubectl create secret generic bbe-observability-alerts -n bbe-observability \
       --from-literal=token='<bot token>' --dry-run=client -o yaml | kubectl apply -f -
     ```
  3. Set the receiver under the `bbe-observability` package's values in `~/.bbe/bbe.yaml`, in [Alertmanager's format](https://prometheus.io/docs/alerting/latest/configuration/#receiver):
     ```yaml
     bbe:
       observability:
         alerts:
           receiver:
             telegram_configs:
               - chat_id: 123456789
                 bot_token_file: /etc/alertmanager/secrets/bbe-observability-alerts/token
     ```
  4. Run `bbe upgrade`.
- **`kubectl top`** works once it's installed, as it adds metrics-server.

## Keeping things up to date

- **Upgrades:** `bbe upgrade` upgrades every installed package, and shows each one's notes again.
- **Your settings are in `~/.bbe/bbe.yaml`.** It includes settings like the seeding ratio or the VPN, written there with their defaults, so a new cluster set up from a copy of it behaves the same.
- **Your secrets aren't in that file.** The VPN keys and the passwords bbe generates stay in the cluster, so keep the VPN keys somewhere safe yourself.
- **Removing a package:** `bbe uninstall <package>`. It lists what it keeps first, such as the files on the NAS, and asks you to confirm.

## When something doesn't work

- **A name doesn't resolve:** check the device uses Blocky for DNS, or that the name is in its hosts file. On Windows, run `ipconfig /flushdns` and restart the browser after changing it.
- **Certificate warnings:** the device doesn't trust the cluster's certificate authority yet (step 4).
- **An app isn't set up yet:** each package's setup runs in the background after an install or upgrade. Its log shows where it is:
  ```
  kubectl logs -n <package> job/<package>-setup-<revision>
  ```
  `kubectl get jobs -n <package>` lists them.
- **Sign-in to an app fails:** check the person is in `users` or `admins` in authentik. A new admin gets their admin rights in the book library within 10 minutes.
