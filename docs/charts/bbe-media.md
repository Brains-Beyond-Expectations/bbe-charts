# bbe-media

**Type:** Umbrella chart  
**Version:** 0.1.1  
**Chart path:** `charts/bbe-media/`

`bbe-media` is a Helm umbrella chart that installs the complete BBE media server stack as a single unit. It bundles both BBE-maintained charts and external upstream charts.

---

## Included Applications

| Application | Chart | Source | Purpose |
|---|---|---|---|
| **Bazarr** | `bazarr 0.1.1` | BBE (internal) | Subtitle manager — auto-downloads subtitles for Sonarr/Radarr |
| **Jellyfin** | `jellyfin 2.3.0` | [jellyfin.github.io/jellyfin-helm](https://jellyfin.github.io/jellyfin-helm) | Media streaming server |
| **Jellyseerr** | `jellyseerr-chart 2.3.3` | `oci://ghcr.io/fallenbagel/jellyseerr` (OCI) | Request management UI for Jellyfin |
| **Prowlarr** | `prowlarr 0.1.3` | BBE (internal) | Indexer manager / proxy for the \*arr stack |
| **Radarr** | `radarr 0.1.2` | BBE (internal) | Movie PVR — finds, downloads, and organises movies |
| **Sonarr** | `sonarr 0.1.2` | BBE (internal) | TV show PVR — finds, downloads, and organises TV series |

---

## Installation

Via bbe-quest CLI (recommended):

```bash
bbe install
# select bbe-media from the list
```

Manually via Helm:

```bash
helm repo add bbe https://brains-beyond-expectations.github.io/bbe-charts
helm install bbe-media bbe/bbe-media
```

---

## Configuration

`bbe-media/values.yaml` is intentionally empty. All configuration is passed through to sub-charts using Helm's standard sub-chart values override mechanism.

To customise a sub-chart, prefix its values with the chart name:

```yaml
# Example: override Radarr's image tag
radarr:
  image:
    tag: "5.22.4"

# Example: enable Sonarr ingress
sonarr:
  ingress:
    enabled: true
    ingressClassName: nginx
    hosts:
      - host: sonarr.homelab.local
        paths:
          - path: /
            pathType: Prefix
```

---

## Sub-chart Documentation

- [bazarr](bazarr.md)
- [prowlarr](prowlarr.md)
- [radarr](radarr.md)
- [sonarr](sonarr.md)
