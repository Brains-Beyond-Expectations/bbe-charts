# bbe-music

![Version: 0.0.1](https://img.shields.io/badge/Version-0.0.1-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square)

A music library for the BBE cluster, with Lidarr to find albums, slskd and Soularr for Soulseek, SoulSync to mirror a Spotify library, and Music Assistant to play it all

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
| bbe.music.slskd.listenPort | int | `50300` | The port Soulseek peers connect to, the same on the router, the address above and slskd |
| bbe.music.slskd.loadBalancerIP | string | `""` | The IP address Soulseek peers reach slskd at, which MetalLB announces on the LAN. Forward the listen port on your router to it, or slskd only reaches peers whose own port is open |
| bbe.music.slskd.resources.limits.memory | string | `"1Gi"` | The memory to limit slskd to |
| bbe.music.slskd.resources.requests.cpu | string | `"50m"` | The CPU to request for slskd |
| bbe.music.slskd.resources.requests.memory | string | `"256Mi"` | The memory to request for slskd |
| bbe.music.slskd.uploadSlots | int | `4` | How many uploads at once. Soulseek expects people to share, and slskd shares the music folder |
| bbe.music.slskd.uploadSpeedLimit | int | `2048` | The upload speed limit, in KiB/s, or 0 for none |
| bbe.music.soularr.allowedFiletypes | string | `"flac 24/192,flac 16/44.1,flac,mp3 320,mp3"` | The formats Soularr takes, best first |
| bbe.music.soularr.image.repository | string | `"mrusse08/soularr"` | The Soularr image, which downloads the albums Lidarr is missing from Soulseek through slskd |
| bbe.music.soularr.image.tag | string | `"latest@sha256:89b6809a169f6c78032c9a66abf5130e4877c46c0b95391818a38ab66cd71548"` | The Soularr version. Its last release is older than main, which `latest` is built from |
| bbe.music.soularr.interval | int | `300` | How long Soularr waits between looking for what Lidarr is missing, in seconds |
| bbe.music.soularr.resources.limits.memory | string | `"512Mi"` | The memory to limit Soularr to |
| bbe.music.soularr.resources.requests.cpu | string | `"20m"` | The CPU to request for Soularr |
| bbe.music.soularr.resources.requests.memory | string | `"128Mi"` | The memory to request for Soularr |
| bbe.music.soulsync.dataSize | string | `"5Gi"` | The size of its data volume, with its settings, database and image cache |
| bbe.music.soulsync.image.repository | string | `"boulderbadgedad/soulsync"` | The SoulSync image, which mirrors a Spotify library track by track from Soulseek and torrents |
| bbe.music.soulsync.image.tag | string | `"3.5.7"` | The SoulSync version. It releases every few days, so it's pinned |
| bbe.music.soulsync.resources.limits.memory | string | `"2Gi"` | The memory to limit SoulSync to |
| bbe.music.soulsync.resources.requests.cpu | string | `"100m"` | The CPU to request for SoulSync |
| bbe.music.soulsync.resources.requests.memory | string | `"512Mi"` | The memory to request for SoulSync |
| bbe.music.user.gid | string | `nil` | The group ID of the NAS user |
| bbe.music.user.uid | string | `nil` | The user ID of the NAS user |
| bbe.setup.backoffLimit | int | `5` | How many times the setup is retried when the apps couldn't be set up |
| bbe.setup.enabled | bool | `true` | Whether to run the Job connecting the apps after every install and upgrade |
| bbe.setup.image.repository | string | `"python"` | The image to run the setup with, which only needs Python |
| bbe.setup.image.tag | string | `"3.13-alpine"` | The tag of the setup image |
| bbe.setup.readyTimeout | int | `900` | How long the setup waits for the apps to start, in seconds |
| bbe.setup.resources.limits.memory | string | `"128Mi"` | The amount of memory to limit the setup pod to |
| bbe.setup.resources.requests.cpu | string | `"50m"` | The amount of CPU to request for the setup pod |
| bbe.setup.resources.requests.memory | string | `"64Mi"` | The amount of memory to request for the setup pod |
| global.bbe.domain | string | `"bbe.home.arpa"` | The domain the cluster's apps are named under, which bbe-networking answers for. Music Assistant is at music.<domain>, and Lidarr, slskd and SoulSync at their own names |
| global.bbe.sso.enabled | bool | `true` | Whether Lidarr, slskd and SoulSync sign people in with bbe-auth's authentik, letting in its `admins` |
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
