# blocky

**Version:** v0.25  
**Ports:** 53 (UDP+TCP, DNS), 4000 (HTTP, API/metrics)  
**Image:** `ghcr.io/0xerr0r/blocky`  
**Chart path:** `charts/blocky/`  
**Part of:** [bbe-networking](bbe-networking.md)

Blocky is a fast, privacy-focused DNS proxy and ad-blocker for the local network. It forwards DNS queries to configurable upstream resolvers while filtering out ad and tracker domains using blocklists.

---

## Installation

Via [bbe-networking](bbe-networking.md) (recommended) or standalone:

```bash
helm repo add bbe https://brains-beyond-expectations.github.io/bbe-charts
helm install blocky bbe/blocky
```

---

## Key Values

```yaml
image:
  repository: ghcr.io/0xerr0r/blocky
  tag: ""           # defaults to Chart appVersion
  pullPolicy: IfNotPresent

service:
  type: LoadBalancer   # Requires MetalLB or another LoadBalancer provider
  dnsPort: 53
  httpPort: 4000

replicas: 2            # Two replicas with podAntiAffinity for HA

ingress:
  enabled: false

resources: {}
env: []
```

---

## Default DNS Configuration

The chart ships with a default Blocky config that:

- Uses **Cloudflare** (`1.1.1.1`) and **Google** (`8.8.8.8`) as upstream DNS resolvers
- Applies the [StevenBlack hosts](https://github.com/StevenBlack/hosts) unified ad+malware blocklist
- Exposes Prometheus metrics on port 4000

---

## High Availability

Blocky runs with `replicas: 2` and `podAntiAffinity` configured to spread pods across nodes. This ensures DNS resolution remains available even if one node goes down.

---

## Prometheus Metrics

Blocky exposes metrics at `http://<service-ip>:4000/metrics`. If Prometheus is installed in the cluster, configure a `ServiceMonitor` or scrape config to collect them.

---

## Notes

- Blocky runs as a `LoadBalancer` service — you must have MetalLB (or equivalent) installed and configure a dedicated IP via the `bbe-networking` chart's `bbe.metallb.blocky.ipAddressPool` value.
- Point your router's DNS server at the LoadBalancer IP to apply ad-blocking network-wide.
