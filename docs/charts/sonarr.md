# sonarr

**Version:** 4.0.14  
**Port:** 8989  
**Image:** `lscr.io/linuxserver/sonarr`  
**Chart path:** `charts/sonarr/`  
**Part of:** [bbe-media](bbe-media.md)

Sonarr is a TV show collection manager (PVR). It monitors RSS feeds, grabs episode releases from configured indexers (via Prowlarr), sends them to download clients, and automatically sorts and renames downloaded files into your media library.

---

## Installation

Via [bbe-media](bbe-media.md) (recommended) or standalone:

```bash
helm repo add bbe https://brains-beyond-expectations.github.io/bbe-charts
helm install sonarr bbe/sonarr
```

---

## Key Values

```yaml
image:
  repository: lscr.io/linuxserver/sonarr
  tag: ""           # defaults to Chart appVersion
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 8989

ingress:
  enabled: false
  ingressClassName: ""
  hosts: []
  tls: []

config:
  enabled: true
  size: 1Gi
  accessMode: ReadWriteOnce
  existingClaim: ""
  retain: false

media:
  enabled: true
  size: 50Gi
  accessMode: ReadWriteOnce
  existingClaim: ""
  retain: false

resources: {}
env: []
replicas: 1
```

---

## Persistent Storage

| PVC | Default Size | Mount Purpose |
|---|---|---|
| `config` | 1Gi | Sonarr configuration, database, and metadata cache |
| `media` | 50Gi | TV library — where downloaded episodes are moved/hardlinked to |

Set `media.existingClaim` to share the media PVC with Radarr or Bazarr so all applications read from the same underlying storage path.
