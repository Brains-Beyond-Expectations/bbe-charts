# bazarr

**Version:** release-1.5.0  
**Port:** 6767  
**Image:** `ghcr.io/hotio/bazarr`  
**Chart path:** `charts/bazarr/`  
**Part of:** [bbe-media](bbe-media.md)

Bazarr is a subtitle manager and companion application for Sonarr and Radarr. It automatically searches for and downloads subtitles for your movies and TV shows from subtitle providers.

---

## Installation

Via [bbe-media](bbe-media.md) (recommended) or standalone:

```bash
helm repo add bbe https://brains-beyond-expectations.github.io/bbe-charts
helm install bazarr bbe/bazarr
```

---

## Key Values

```yaml
image:
  repository: ghcr.io/hotio/bazarr
  tag: ""           # defaults to Chart appVersion
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 6767

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
| `config` | 1Gi | Bazarr configuration and database |
| `media` | 50Gi | Shared media directory (must match Sonarr/Radarr mount path) |

Set `media.existingClaim` to use the same PVC already mounted by Sonarr or Radarr for correct subtitle file placement.
