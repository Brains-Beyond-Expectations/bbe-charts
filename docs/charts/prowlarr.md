# prowlarr

**Version:** 1.35.1  
**Port:** 9696  
**Image:** `lscr.io/linuxserver/prowlarr`  
**Chart path:** `charts/prowlarr/`  
**Part of:** [bbe-media](bbe-media.md)

Prowlarr is an indexer manager and proxy for the \*arr ecosystem. It centralises tracker and indexer configuration, syncing them automatically to Sonarr, Radarr, and other supported applications. Eliminates the need to configure indexers in each \*arr app individually.

---

## Installation

Via [bbe-media](bbe-media.md) (recommended) or standalone:

```bash
helm repo add bbe https://brains-beyond-expectations.github.io/bbe-charts
helm install prowlarr bbe/prowlarr
```

---

## Key Values

```yaml
image:
  repository: lscr.io/linuxserver/prowlarr
  tag: ""           # defaults to Chart appVersion
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 9696

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

resources: {}
env: []
replicas: 1
```

---

## Persistent Storage

A `config` PVC (`1Gi`, `ReadWriteOnce`) stores Prowlarr's database and configuration, including indexer credentials and sync state.
