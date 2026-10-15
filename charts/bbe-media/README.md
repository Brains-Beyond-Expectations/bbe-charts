# bbe-media

![Version: 0.2.0](https://img.shields.io/badge/Version-0.2.0-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square)

A collection of charts for BBE cluster media, connected to each other when installed

**Homepage:** <https://brains-beyond-expectations.github.io/bbe-charts>

## Requirements

| Repository | Name | Version |
|------------|------|---------|
| https://brains-beyond-expectations.github.io/bbe-charts | bazarr | 0.4.0 |
| https://brains-beyond-expectations.github.io/bbe-charts | prowlarr | 0.4.0 |
| https://brains-beyond-expectations.github.io/bbe-charts | qbittorrent | 0.1.0 |
| https://brains-beyond-expectations.github.io/bbe-charts | radarr | 0.4.0 |
| https://brains-beyond-expectations.github.io/bbe-charts | sonarr | 0.4.0 |
| https://jellyfin.github.io/jellyfin-helm | jellyfin | 3.2.0 |
| oci://ghcr.io/seerr-team/seerr | seerr-chart | 3.9.1 |

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| bazarr.bazarr.env[0].name | string | `"DYNACONF_AUTH__APIKEY"` |  |
| bazarr.bazarr.env[0].valueFrom.secretKeyRef.key | string | `"bazarr"` |  |
| bazarr.bazarr.env[0].valueFrom.secretKeyRef.name | string | `"bbe-media-api-keys"` |  |
| bazarr.bazarr.env[1].name | string | `"PUID"` |  |
| bazarr.bazarr.env[1].valueFrom.configMapKeyRef.key | string | `"PUID"` |  |
| bazarr.bazarr.env[1].valueFrom.configMapKeyRef.name | string | `"bbe-media-user"` |  |
| bazarr.bazarr.env[2].name | string | `"PGID"` |  |
| bazarr.bazarr.env[2].valueFrom.configMapKeyRef.key | string | `"PGID"` |  |
| bazarr.bazarr.env[2].valueFrom.configMapKeyRef.name | string | `"bbe-media-user"` |  |
| bazarr.media.existingClaim | string | `"bbe-media-library"` |  |
| bbe.admin.username | string | `"admin"` | The username for every app's web UI. Its password is generated into the `bbe-media-admin` secret |
| bbe.media.bazarr.languages | list | `["en"]` | The languages Bazarr downloads subtitles in, as two-letter codes. The setup puts them in a languages profile named `bbe`, which new series and movies get unless Bazarr has another default, and so do those without one. Empty for no profile |
| bbe.media.bazarr.providers | list | `[]` | The subtitle providers bbe turns on in Bazarr, besides those turned on in Bazarr. Add them with `bbe configure bbe-media`, each with the `name` Bazarr knows it by. Removing one here doesn't turn it off |
| bbe.media.flaresolverr.enabled | bool | `true` | Whether to run FlareSolverr, which Prowlarr sends an indexer's requests through when Cloudflare challenges them. The setup tags every indexer it adds for it |
| bbe.media.flaresolverr.image.repository | string | `"ghcr.io/flaresolverr/flaresolverr"` | The FlareSolverr image |
| bbe.media.flaresolverr.image.tag | string | `"v3.5.2"` | The FlareSolverr image tag |
| bbe.media.flaresolverr.requestTimeout | int | `60` | How long FlareSolverr may take to get past a challenge, in seconds, from 1 to 180 |
| bbe.media.flaresolverr.resources.limits.memory | string | `"1Gi"` | The memory to limit FlareSolverr to |
| bbe.media.flaresolverr.resources.requests.cpu | string | `"50m"` | The CPU to request for FlareSolverr |
| bbe.media.flaresolverr.resources.requests.memory | string | `"256Mi"` | The memory to request for FlareSolverr, which runs Chromium |
| bbe.media.ingress.enabled | bool | `true` | Whether to serve every app at <app>.<domain>, through bbe-networking's Traefik |
| bbe.media.nfs.mountOptions | list | `["nfsvers=4"]` | Mount options for the NFS share. NFSv4 needs no lock daemon, which Talos nodes don't run, and `nfsvers=4` uses the newest NFSv4 version the server offers, such as 4.0 on Synology NAS where 4.1 isn't offered |
| bbe.media.nfs.path | string | `""` | The exported path of the media library on the NFS server |
| bbe.media.nfs.server | string | `""` | The NFS server holding the media library, as a hostname or IP address |
| bbe.media.prowlarr.indexers | list | `[]` | The indexers Prowlarr searches, and shares with Sonarr and Radarr. Add them with `bbe configure bbe-media`. Each has the `name` it gets in Prowlarr, the Prowlarr `definition` it's made from, its `fields`, and in `secretFields` the key in the `bbe-media-indexers` secret of each field that's a credential |
| bbe.media.size | string | `"1Ti"` | The size of the media library. NFS doesn't enforce it, but Kubernetes needs one |
| bbe.media.user.gid | string | `nil` | The group ID of the NAS user owning the media library share |
| bbe.media.user.uid | string | `nil` | The user ID of the NAS user owning the media library share |
| bbe.setup.backoffLimit | int | `5` | How many times the setup is retried when an app couldn't be set up |
| bbe.setup.enabled | bool | `true` | Whether to connect the apps to each other after every install and upgrade |
| bbe.setup.image.repository | string | `"python"` | The image to run the setup with, which only needs Python |
| bbe.setup.image.tag | string | `"3.13-alpine"` | The tag of the setup image |
| bbe.setup.readyTimeout | int | `900` | How long the setup waits for the apps to start, in seconds |
| bbe.setup.resources.limits.memory | string | `"128Mi"` | The amount of memory to limit the setup pod to |
| bbe.setup.resources.requests.cpu | string | `"50m"` | The amount of CPU to request for the setup pod |
| bbe.setup.resources.requests.memory | string | `"64Mi"` | The amount of memory to request for the setup pod |
| global.bbe.domain | string | `"bbe.home.arpa"` | The domain the apps are named under, such as sonarr.bbe.home.arpa, the same as bbe-networking's |
| global.bbe.sso.enabled | bool | `true` | Whether people sign in with bbe-auth's authentik. The apps managing the media are behind its forward auth, for admins, and skip their own logins, which only bbe's setup and the apps' connections to each other use. Jellyfin signs people in against its LDAP, and Seerr through Jellyfin |
| jellyfin.image.repository | string | `"lscr.io/linuxserver/jellyfin"` |  |
| jellyfin.image.tag | string | `"12.2ubu2604-ls53"` |  |
| jellyfin.jellyfin.env[0].name | string | `"PUID"` |  |
| jellyfin.jellyfin.env[0].valueFrom.configMapKeyRef.key | string | `"PUID"` |  |
| jellyfin.jellyfin.env[0].valueFrom.configMapKeyRef.name | string | `"bbe-media-user"` |  |
| jellyfin.jellyfin.env[1].name | string | `"PGID"` |  |
| jellyfin.jellyfin.env[1].valueFrom.configMapKeyRef.key | string | `"PGID"` |  |
| jellyfin.jellyfin.env[1].valueFrom.configMapKeyRef.name | string | `"bbe-media-user"` |  |
| jellyfin.persistence.cache.enabled | bool | `true` |  |
| jellyfin.persistence.cache.size | string | `"2Gi"` |  |
| jellyfin.persistence.config.size | string | `"3Gi"` |  |
| jellyfin.persistence.media.existingClaim | string | `"bbe-media-library"` |  |
| jellyfin.volumeMounts[0].mountPath | string | `"/transcode"` |  |
| jellyfin.volumeMounts[0].name | string | `"cache"` |  |
| prowlarr.prowlarr.env[0].name | string | `"PROWLARR__AUTH__APIKEY"` |  |
| prowlarr.prowlarr.env[0].valueFrom.secretKeyRef.key | string | `"prowlarr"` |  |
| prowlarr.prowlarr.env[0].valueFrom.secretKeyRef.name | string | `"bbe-media-api-keys"` |  |
| qbittorrent.extraContainers | string | `"{{- if .Values.global.bbe.sso.enabled }}\n- name: sso\n  image: nginxinc/nginx-unprivileged:1.29-alpine\n  ports:\n    - name: sso\n      containerPort: 4180\n  readinessProbe:\n    tcpSocket:\n      port: sso\n  resources:\n    requests:\n      memory: 16Mi\n      cpu: 10m\n    limits:\n      memory: 64Mi\n  securityContext:\n    runAsNonRoot: true\n    runAsUser: 101\n    runAsGroup: 101\n    allowPrivilegeEscalation: false\n    capabilities:\n      drop:\n        - ALL\n  volumeMounts:\n    - name: sso\n      mountPath: /etc/nginx/conf.d\n      readOnly: true\n{{- end }}\n"` |  |
| qbittorrent.extraVolumes | string | `"{{- if .Values.global.bbe.sso.enabled }}\n- name: sso\n  configMap:\n    name: {{ .Release.Name }}-qbittorrent-sso\n{{- end }}\n"` |  |
| qbittorrent.incomplete.enabled | bool | `true` |  |
| qbittorrent.incomplete.size | string | `"20Gi"` | The node storage for downloads in progress. Downloads that don't fit together wait until others complete |
| qbittorrent.media.existingClaim | string | `"bbe-media-library"` |  |
| qbittorrent.qbittorrent.env[0].name | string | `"PUID"` |  |
| qbittorrent.qbittorrent.env[0].valueFrom.configMapKeyRef.key | string | `"PUID"` |  |
| qbittorrent.qbittorrent.env[0].valueFrom.configMapKeyRef.name | string | `"bbe-media-user"` |  |
| qbittorrent.qbittorrent.env[1].name | string | `"PGID"` |  |
| qbittorrent.qbittorrent.env[1].valueFrom.configMapKeyRef.key | string | `"PGID"` |  |
| qbittorrent.qbittorrent.env[1].valueFrom.configMapKeyRef.name | string | `"bbe-media-user"` |  |
| qbittorrent.qbittorrent.webui.apiKeyKey | string | `"qbittorrent"` |  |
| qbittorrent.qbittorrent.webui.apiKeySecret | string | `"bbe-media-api-keys"` |  |
| qbittorrent.qbittorrent.webui.existingSecret | string | `"bbe-media-admin"` |  |
| qbittorrent.qbittorrent.webui.localHostAuth | bool | `false` |  |
| qbittorrent.service.extraPorts | string | `"{{- if .Values.global.bbe.sso.enabled }}\n- name: sso\n  port: 4180\n  protocol: TCP\n{{- end }}\n"` |  |
| radarr.media.existingClaim | string | `"bbe-media-library"` |  |
| radarr.radarr.env[0].name | string | `"RADARR__AUTH__APIKEY"` |  |
| radarr.radarr.env[0].valueFrom.secretKeyRef.key | string | `"radarr"` |  |
| radarr.radarr.env[0].valueFrom.secretKeyRef.name | string | `"bbe-media-api-keys"` |  |
| radarr.radarr.env[1].name | string | `"PUID"` |  |
| radarr.radarr.env[1].valueFrom.configMapKeyRef.key | string | `"PUID"` |  |
| radarr.radarr.env[1].valueFrom.configMapKeyRef.name | string | `"bbe-media-user"` |  |
| radarr.radarr.env[2].name | string | `"PGID"` |  |
| radarr.radarr.env[2].valueFrom.configMapKeyRef.key | string | `"PGID"` |  |
| radarr.radarr.env[2].valueFrom.configMapKeyRef.name | string | `"bbe-media-user"` |  |
| seerr-chart.config.persistence.size | string | `"1Gi"` |  |
| seerr-chart.image.tag | string | `"v3.5.0"` |  |
| sonarr.media.existingClaim | string | `"bbe-media-library"` |  |
| sonarr.sonarr.env[0].name | string | `"SONARR__AUTH__APIKEY"` |  |
| sonarr.sonarr.env[0].valueFrom.secretKeyRef.key | string | `"sonarr"` |  |
| sonarr.sonarr.env[0].valueFrom.secretKeyRef.name | string | `"bbe-media-api-keys"` |  |
| sonarr.sonarr.env[1].name | string | `"PUID"` |  |
| sonarr.sonarr.env[1].valueFrom.configMapKeyRef.key | string | `"PUID"` |  |
| sonarr.sonarr.env[1].valueFrom.configMapKeyRef.name | string | `"bbe-media-user"` |  |
| sonarr.sonarr.env[2].name | string | `"PGID"` |  |
| sonarr.sonarr.env[2].valueFrom.configMapKeyRef.key | string | `"PGID"` |  |
| sonarr.sonarr.env[2].valueFrom.configMapKeyRef.name | string | `"bbe-media-user"` |  |

----------------------------------------------
Autogenerated from chart metadata using [helm-docs v1.14.2](https://github.com/norwoodj/helm-docs/releases/v1.14.2)
