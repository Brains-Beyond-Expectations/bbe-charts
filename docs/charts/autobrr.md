# autobrr

**Version:** v1.62  
**Port:** 7474  
**Image:** `ghcr.io/autobrr/autobrr`  
**Chart path:** `charts/autobrr/`

autobrr is a modern download automation tool for torrents and Usenet. It monitors RSS feeds, IRC announce channels, and other sources, then triggers downloads on configured download clients based on user-defined filters.

---

## Installation

```bash
helm repo add bbe https://brains-beyond-expectations.github.io/bbe-charts
helm install autobrr bbe/autobrr
```

---

## Key Values

```yaml
image:
  repository: ghcr.io/autobrr/autobrr
  tag: ""           # defaults to Chart appVersion
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 7474

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

A `PersistentVolumeClaim` named `config` is created by default (`1Gi`, `ReadWriteOnce`) and mounted at the autobrr config path. Set `config.existingClaim` to reuse an existing PVC.

Set `config.retain: true` to use a `Retain` reclaim policy so data survives chart uninstallation.
