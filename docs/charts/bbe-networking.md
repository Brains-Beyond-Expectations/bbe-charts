# bbe-networking

**Type:** Umbrella chart  
**Version:** 0.1.0  
**Chart path:** `charts/bbe-networking/`

`bbe-networking` is a Helm umbrella chart that installs the complete BBE network infrastructure stack. It includes a DNS ad-blocker, a LoadBalancer provider, and an Ingress controller, plus MetalLB IP address pool configuration.

---

## Included Applications

| Application | Chart | Source | Purpose |
|---|---|---|---|
| **Blocky** | `blocky 1.1.1` | BBE (internal) | DNS proxy and ad-blocker for the local network |
| **ingress-nginx** | `ingress-nginx 4.12.1` | [kubernetes.github.io/ingress-nginx](https://kubernetes.github.io/ingress-nginx) | Kubernetes Ingress controller |
| **MetalLB** | `metallb 0.14.9` | [metallb.github.io/metallb](https://metallb.github.io/metallb) | LoadBalancer IP address allocator for bare-metal clusters |

---

## Additional Resources

Beyond the sub-chart installations, `bbe-networking` creates MetalLB custom resources via its own templates:

| Template | Resource | Purpose |
|---|---|---|
| `metallb-ip-address-pool-blocky.yaml` | `IPAddressPool` + `L2Advertisement` | Dedicated IP pool for Blocky's DNS LoadBalancer service |
| `metallb-ip-address-pool-default.yaml` | `IPAddressPool` + `L2Advertisement` | Default IP pool for the ingress-nginx LoadBalancer |

---

## Installation

Via bbe-quest CLI (recommended):

```bash
bbe install
# select bbe-networking from the list
```

Manually via Helm:

```bash
helm repo add bbe https://brains-beyond-expectations.github.io/bbe-charts
helm install bbe-networking bbe/bbe-networking
```

---

## Required Configuration

The following values **must** be set before installing:

```yaml
bbe:
  metallb:
    blocky:
      ipAddressPool: "192.168.1.50-192.168.1.50"  # Static IP for Blocky DNS

ingress-nginx:
  controller:
    service:
      loadBalancerIP: "192.168.1.51"              # Static IP for ingress-nginx
```

---

## Default Configuration

The chart ships with opinionated defaults:

- **MetalLB speaker**: `ignoreExcludeLB: true`
- **ingress-nginx**: 
  - Service type `LoadBalancer`
  - Allows snippet annotations (`Critical` risk level)
  - `nginx` registered as the default `IngressClass`
  - Prometheus `ServiceMonitor` enabled
- **Blocky**: See [blocky chart documentation](blocky.md) for default DNS upstream and ad-block list configuration

---

## Sub-chart Documentation

- [blocky](blocky.md)
