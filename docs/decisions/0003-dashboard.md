# 0003: A dashboard as the cluster's landing page

**Status:** proposed, 2026-10-14

## Context

Each package adds apps, each at its own address under the cluster's domain (`<app>.bbe.home.arpa`). As packages are added, remembering what's installed and where it is gets harder, especially for people who didn't install it ([#147](https://github.com/Brains-Beyond-Expectations/bbe-charts/issues/147)).

The issue's requirements:
- **Required:** it's configured by code, and costs the cluster little.
- **Nice to have:** it finds the apps by itself, it's Kubernetes-native, and it shows whether they're up.

## Decisions

### 1. Homepage

[Homepage](https://gethomepage.dev) (v2.5.0) is the only one of the issue's candidates meeting every requirement and nice-to-have:
- It's configured by YAML files.
- It runs as one small pod.
- It finds apps from `gethomepage.dev/*` annotations on Ingresses (and Traefik IngressRoutes) in every namespace.
- It shows whether their pods run.

The others fall short:
- **Homer** is static, with no discovery, so every app would need a change in its config.
- **Dashy** is heavier, with no Kubernetes discovery.
- **Heimdall** and **Organizr** are configured in their UI and keep it in their own database, not in code.

Homepage's only Helm chart is unofficial and was last updated in May 2025. So `bbe-networking` follows the manifests in Homepage's own Kubernetes docs instead: a Deployment, a ConfigMap, and a ClusterRole that only gets and lists namespaces, pods, nodes, Ingresses and IngressRoutes.

### 2. It's part of bbe-networking, at the domain itself

The dashboard answers at `https://<domain>`, which Blocky already resolves and the domain's certificate already covers.
- `bbe-networking` owns how anything in the cluster is reached: the domain, DNS, certificates and Traefik. Every cluster where apps have addresses has it, so the landing page is there by default (`bbe.dashboard.enabled`).
- Packages don't depend on the dashboard. They annotate their own Ingresses, and appear once they're installed. Adding a tool never changes the dashboard.

| Annotation | |
|---|---|
| `gethomepage.dev/enabled: "true"` | Lists the app |
| `gethomepage.dev/name`, `description`, `icon` | How it's shown. Icons are names from Homepage's icon set |
| `gethomepage.dev/group` | `Watch` (apps for everyone), `Manage` (apps managing the media) or `Cluster`, ordered by `bbe.dashboard.settings` |
| `gethomepage.dev/pod-selector` | The pods whose status is shown, when their labels don't match the Ingress' name |

Rejected:
- **A `bbe-dashboard` package.** It would be one more thing to choose in `bbe install`, so it wouldn't be the default.
- **Inside `bbe-auth`.** It would be behind single sign-on from the start, but clusters without `bbe-auth` would have no dashboard.

### 3. Links and status only, open on the network

`bbe-auth` depends on `bbe-networking`, so the dashboard can't be behind single sign-on without the two needing each other. It shows links and whether pods run, which is little to give away on the local network. The apps behind the links still ask for their sign-in.

Homepage's widgets showing an app's own data, such as Sonarr's queue, would call the app's API with its key, and show the result to anyone reaching the dashboard. They're left out until the dashboard can sit behind single sign-on. Its Kubernetes widgets need metrics-server, which Talos doesn't run by default, so they're left out too.

## Consequences

- **The dashboard lists every annotated Ingress in the cluster, from any package,** so annotating an Ingress is part of adding a tool.
- **It's open to anyone on the network**, like Blocky and the apps' sign-in pages.
- **Icons load from Homepage's icon CDN**, so a device without internet access shows the apps without icons.
- **Not verified on a cluster**, as the test cluster was torn down. The templates follow Homepage v2.5.0's own Kubernetes manifests, and are covered by unit tests.
