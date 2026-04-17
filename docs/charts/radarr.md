# radarr

**Version:** 5.22.4  
**Port:** 7878  
**Image:** `lscr.io/linuxserver/radarr`  
**Chart path:** `charts/radarr/`  
**Part of:** [bbe-media](bbe-media.md)

Radarr is a movie collection manager (PVR). It monitors RSS feeds, grabs movie releases from configured indexers (via Prowlarr), sends them to download clients, and then automatically sorts and renames downloaded files into your media library.

---

## Installation

Via [bbe-media](bbe-media.md) (recommended) or standalone:

```bash
helm repo add bbe https://brains-beyond-expectations.github.io/bbe-charts
helm install radarr bbe/radarr
```

---

## Key Values

```yaml
image:
  repository: lscr.io/linuxserver/radarr
  tag: ""           # defaults to Chart appVersion
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 7878

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
| `config` | 1Gi | Radarr configuration, database, and metadata cache |
| `media` | 50Gi | Movie library — where downloaded files are moved/hardlinked to |

Set `media.existingClaim` to share the media PVC with Bazarr or other \*arr apps so they all read from the same underlying storage path.
