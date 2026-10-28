# bbe-music

![Version: 0.0.1](https://img.shields.io/badge/Version-0.0.1-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square)

A music library for the BBE cluster, with Lidarr to find albums, slskd for Soulseek, SoulSync to mirror a Spotify library and import Soulseek downloads, and Music Assistant to play it all

**Homepage:** <https://brains-beyond-expectations.github.io/bbe-charts>

## Requirements

| Repository | Name | Version |
|------------|------|---------|
| https://brains-beyond-expectations.github.io/bbe-charts | lidarr | 0.0.1 |

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| bbe.admin.username | string | `"music-admin"` | Music Assistant's admin username |
| bbe.ingress.enabled | bool | `true` | Whether to serve the apps at their names under the domain through bbe-networking's Traefik |
| bbe.music.lidarr.metadataProfile | string | `"Standard"` | The metadata profile Lidarr gets new artists with: `Standard` or `None` |
| bbe.music.lidarr.qualityProfile | string | `"Any"` | The quality profile Lidarr gets new artists with: `Any`, `Lossless` or `Standard` |
| bbe.music.musicAssistant.dataSize | string | `"5Gi"` | The size of its data volume, with its settings, database and artwork cache |
| bbe.music.musicAssistant.image.repository | string | `"ghcr.io/music-assistant/server"` | The Music Assistant server image |
| bbe.music.musicAssistant.image.tag | string | `"2.10.7"` | The Music Assistant version. Stable and beta mustn't share one data volume |
| bbe.music.musicAssistant.resources.limits.memory | string | `"2Gi"` | The memory to limit Music Assistant to. Its docs ask for 2Gi at least |
| bbe.music.musicAssistant.resources.requests.cpu | string | `"100m"` | The CPU to request for Music Assistant |
| bbe.music.musicAssistant.resources.requests.memory | string | `"512Mi"` | The memory to request for Music Assistant |
| bbe.music.nfs.mountOptions | list | `["nfsvers=4"]` | Mount options for the NFS share. NFSv4 needs no lock daemon, which Talos nodes don't run, and `nfsvers=4` uses the newest NFSv4 version the server offers |
| bbe.music.nfs.path | string | `""` | The exported path holding the music on the NFS server. Best bbe-media's share, as the music gets folders of its own |
| bbe.music.nfs.server | string | `""` | The NFS server holding the music, as a hostname or IP address. Best bbe-media's, as Lidarr then finds qBittorrent's downloads where qBittorrent left them, and hardlinks them |
| bbe.music.seedRatio | int | `2` | The ratio SoulSync's torrents seed to before qBittorrent removes them, like bbe-media's `bbe.media.seeding.maxRatio`, or 0 for SoulSync's own default |
| bbe.music.size | string | `"1Ti"` | The size of the share. NFS doesn't enforce it, but Kubernetes needs one |
| bbe.music.slskd.dataSize | string | `"2Gi"` | The size of its data volume, with its database and search history |
| bbe.music.slskd.image.repository | string | `"slskd/slskd"` | The slskd image, a Soulseek client with a web interface and API |
| bbe.music.slskd.image.tag | string | `"0.26.1"` | The slskd version |
| bbe.music.slskd.listenPort | int | `50300` | The port slskd listens on for Soulseek peers, the same on the router and the address above. With the VPN, the port it forwards is used instead |
| bbe.music.slskd.loadBalancerIP | string | `""` | Without the VPN, an IP address on your LAN for Soulseek peers to reach slskd at, which MetalLB announces. Forward the listen port on your router to it. Left empty, slskd only reaches peers whose own port is open |
| bbe.music.slskd.resources.limits.memory | string | `"1Gi"` | The memory to limit slskd to |
| bbe.music.slskd.resources.requests.cpu | string | `"50m"` | The CPU to request for slskd |
| bbe.music.slskd.resources.requests.memory | string | `"256Mi"` | The memory to request for slskd |
| bbe.music.slskd.uploadSlots | int | `4` | How many uploads at once. Soulseek expects people to share, and slskd shares the music folder |
| bbe.music.slskd.uploadSpeedLimit | int | `2048` | The upload speed limit, in KiB/s, or 0 for none |
| bbe.music.soulsync.dataSize | string | `"5Gi"` | The size of its data volume, with its settings, database and image cache |
| bbe.music.soulsync.image.repository | string | `"boulderbadgedad/soulsync"` | The SoulSync image, which mirrors a Spotify library track by track from Soulseek and torrents |
| bbe.music.soulsync.image.tag | string | `"3.5.7"` | The SoulSync version. It releases every few days, so it's pinned |
| bbe.music.soulsync.resources.limits.memory | string | `"2Gi"` | The memory to limit SoulSync to |
| bbe.music.soulsync.resources.requests.cpu | string | `"100m"` | The CPU to request for SoulSync |
| bbe.music.soulsync.resources.requests.memory | string | `"512Mi"` | The memory to request for SoulSync |
| bbe.music.user.gid | string | `nil` | The group ID of the NAS user |
| bbe.music.user.uid | string | `nil` | The user ID of the NAS user |
| bbe.networkPolicy.enabled | bool | `true` | Whether only Traefik and the apps themselves may reach the apps, besides bbe-media's Prowlarr reaching Lidarr, and Soulseek peers reaching slskd without the VPN. The cluster's network has to enforce NetworkPolicies, which `bbe setup` turns on for the clusters it creates |
| bbe.setup.backoffLimit | int | `10` | How many times the setup is retried when the apps couldn't be set up |
| bbe.setup.enabled | bool | `true` | Whether to run the Job connecting the apps after every install and upgrade |
| bbe.setup.image.repository | string | `"python"` | The image to run the setup with, which only needs Python |
| bbe.setup.image.tag | string | `"3.13-alpine"` | The tag of the setup image |
| bbe.setup.readyTimeout | int | `1800` | How long the setup waits for the apps to start, in seconds |
| bbe.setup.resources.limits.memory | string | `"128Mi"` | The amount of memory to limit the setup pod to |
| bbe.setup.resources.requests.cpu | string | `"50m"` | The amount of CPU to request for the setup pod |
| bbe.setup.resources.requests.memory | string | `"64Mi"` | The amount of memory to request for the setup pod |
| bbe.setup.retryDelay | int | `300` | How long a failed setup waits before it's retried, in seconds. Kubernetes waits too, from 10 seconds at first, doubling up to 6 minutes |
| global.bbe.domain | string | `"bbe.home.arpa"` | The domain the cluster's apps are named under, which bbe-networking answers for. Music Assistant is at music.<domain>, and Lidarr, slskd and SoulSync at their own names |
| global.bbe.sso.enabled | bool | `true` | Whether Lidarr, slskd and SoulSync sign people in with bbe-auth's authentik, letting in its `admins` |
| global.bbe.vpn.clusterDns | string | `"10.96.0.10"` | The cluster's DNS, which gluetun sends cluster names to. Everything else is resolved through the tunnel |
| global.bbe.vpn.enabled | bool | `false` | Whether slskd's traffic goes through the VPN. Needs bbe-media's `bbe-vpn` Secret |
| global.bbe.vpn.image | string | `"qmcgaw/gluetun:v3.41.3@sha256:fa19cc76b2af13d57a8d3dc3066f2ada061b1c761b8aecf989b3877c0486e027"` | The gluetun image |
| global.bbe.vpn.podSubnet | string | `"10.244.0.0/16"` | The cluster's pod network, reachable outside the tunnel |
| global.bbe.vpn.provider | string | `"protonvpn"` | The VPN provider, as gluetun names it. Its port forwarding lets Soulseek peers reach slskd through the VPN |
| global.bbe.vpn.secret | string | `"bbe-vpn"` | bbe-media's Secret with a WireGuard private key for each app, which bbe-music copies slskd's from |
| global.bbe.vpn.serverCountries | string | `""` | The countries of the servers to use, comma-separated, or any with port forwarding when empty |
| global.bbe.vpn.serviceSubnet | string | `"10.96.0.0/12"` | The cluster's Service network, reachable outside the tunnel |
| lidarr.lidarr.env[0].name | string | `"LIDARR__AUTH__APIKEY"` |  |
| lidarr.lidarr.env[0].valueFrom.secretKeyRef.key | string | `"lidarr"` |  |
| lidarr.lidarr.env[0].valueFrom.secretKeyRef.name | string | `"bbe-music-api-keys"` |  |
| lidarr.lidarr.env[1].name | string | `"PUID"` |  |
| lidarr.lidarr.env[1].valueFrom.configMapKeyRef.key | string | `"PUID"` |  |
| lidarr.lidarr.env[1].valueFrom.configMapKeyRef.name | string | `"bbe-music-user"` |  |
| lidarr.lidarr.env[2].name | string | `"PGID"` |  |
| lidarr.lidarr.env[2].valueFrom.configMapKeyRef.key | string | `"PGID"` |  |
| lidarr.lidarr.env[2].valueFrom.configMapKeyRef.name | string | `"bbe-music-user"` |  |
| lidarr.media.existingClaim | string | `"bbe-music-share"` |  |

----------------------------------------------
Autogenerated from chart metadata using [helm-docs v1.14.2](https://github.com/norwoodj/helm-docs/releases/v1.14.2)
