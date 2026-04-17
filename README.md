# BBE Charts

Helm charts for the **Brains Beyond Expectations** home-lab platform. This repository provides the Kubernetes application charts installed and managed by the [bbe-quest](https://github.com/Brains-Beyond-Expectations/bbe-quest) CLI.

Charts are hosted at `https://brains-beyond-expectations.github.io/bbe-charts`.

## Installable Packages

| Package | Description |
|---|---|
| [`bbe-media`](docs/charts/bbe-media.md) | Full media server stack — Jellyfin, Sonarr, Radarr, Prowlarr, Bazarr, Jellyseerr |
| [`bbe-networking`](docs/charts/bbe-networking.md) | Network infrastructure — MetalLB, ingress-nginx, Blocky DNS ad-blocker |

## Quick Start (via bbe-quest)

```bash
bbe install   # select bbe-media and/or bbe-networking
```

## Manual Helm Usage

```bash
helm repo add bbe https://brains-beyond-expectations.github.io/bbe-charts
helm repo update
helm search repo bbe

helm install bbe-media bbe/bbe-media
helm install bbe-networking bbe/bbe-networking
```

## Documentation

- [Architecture](docs/architecture.md) — how charts are structured and how bbe-quest consumes them
- [Library Versioning](docs/library-versioning.md) — how `library.yaml` is generated and versioned
- [Development](docs/development.md) — how to add charts, run tests, and release updates

### Charts

**Umbrella charts (installable via `bbe install`):**
- [bbe-media](docs/charts/bbe-media.md)
- [bbe-networking](docs/charts/bbe-networking.md)

**Individual application charts:**
- [autobrr](docs/charts/autobrr.md) — download automation
- [bazarr](docs/charts/bazarr.md) — subtitle manager
- [blocky](docs/charts/blocky.md) — DNS proxy and ad-blocker
- [prowlarr](docs/charts/prowlarr.md) — indexer manager
- [radarr](docs/charts/radarr.md) — movie PVR
- [sonarr](docs/charts/sonarr.md) — TV show PVR

## Related

- [bbe-quest](https://github.com/Brains-Beyond-Expectations/bbe-quest) — the CLI that installs and manages these charts on your cluster
