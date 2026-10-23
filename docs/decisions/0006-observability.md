# 0006: Metrics, logs and alerts

**Status:** proposed, 2026-10-22

## Context

Nothing tells anyone when something in the cluster goes wrong. A Longhorn volume losing its only copy, a disk filling up, or the domain's certificate failing to renew only shows when an app stops working. Finding out why then means reading pods' logs with kubectl, and only for as long as the pod still exists.

The goal is one package, `bbe-observability`, which:
- keeps the cluster's metrics and the apps' logs for a couple of weeks;
- alerts on what's particular to a BBE cluster, and sends alerts where people will see them;
- shows all of it in one place, behind the same sign-in as the other apps;
- costs a home lab little, and needs nothing to be set before it's installed.

## Decisions

### 1. kube-prometheus-stack, Loki, Alloy and metrics-server, from their own charts

`bbe-observability` depends on four charts, as `bbe-networking` does on Traefik's and cert-manager's:

| Chart | Version | What it runs |
|---|---|---|
| [kube-prometheus-stack](https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack) | 92.11.0 | The Prometheus operator, Prometheus, Alertmanager, Grafana, node-exporter and kube-state-metrics, with their dashboards and rules |
| [loki](https://github.com/grafana/loki/tree/main/production/helm/loki) | 7.5.0 | Loki in one pod, keeping logs on a Longhorn volume |
| [alloy](https://github.com/grafana/alloy/tree/main/operations/helm) | 1.14.2 | Grafana Alloy on every node, sending the logs of its pods to Loki |
| [metrics-server](https://github.com/kubernetes-sigs/metrics-server) | 3.14.0 | `kubectl top`, and the Kubernetes widgets of the dashboard ([0003](0003-dashboard.md), decision 3) |

The whole package asks for about 1.2Gi of memory on one node, and may use up to about 4Gi, most of it Prometheus and Loki. Metrics are kept for 15 days or 8GB on a 10Gi volume, and logs for 15 days on another.

Loki runs as a single binary with its filesystem storage, without its gateway, caches, canary or tests. They only pay off on bigger clusters, and the caches alone would ask for more memory than the rest of the package.

Alloy reads the pods' log files under `/var/log/pods` on each node, and finds which pod each belongs to through the Kubernetes API, only for the pods on its own node. It runs as root to read them.

Rejected:
- **VictoriaMetrics and VictoriaLogs**, which use less memory. kube-prometheus-stack's dashboards and rules are what most guides and examples assume, and the Prometheus operator's ServiceMonitors are what other charts ship.
- **Promtail**, which Grafana deprecated in favour of Alloy.
- **Reading logs through the Kubernetes API** (`loki.source.kubernetes`), which needs no host folder. Every line would go through the API server, and logs would only be read while the API answers.

### 2. Grafana is behind authentik, for admins

Grafana is served at `grafana.<domain>` through Traefik, behind authentik's forward auth, like Sonarr ([0002](0002-single-sign-on.md), decision 7). authentik's forward auth only lets `admins` through.

Grafana signs them in from the headers authentik passes on (`auth.proxy`): `X-authentik-username`, with their email and name. It makes an account for each the first time, as an admin. Its own login form and basic auth are off, so its generated `admin` account, in the `bbe-observability-grafana` secret, signs nobody in.

Grafana keeps what's made in it, such as dashboards and preferences, on a 1Gi volume. The data sources, Prometheus and Loki, and kube-prometheus-stack's dashboards are provisioned on every start.

Rejected: **OpenID Connect**, like Shelfmark ([0004](0004-book-library.md)). It would need a provider in bbe-auth's blueprint, so bbe-auth would change whenever bbe-observability did. Forward auth needs nothing in bbe-auth, as it covers everything under the domain.

### 3. The monitors live here

Prometheus finds ServiceMonitors, PodMonitors and rules in every namespace, whichever chart made them. `bbe-observability` makes the ones for the other packages itself, so those don't need the operator's CRDs:

| Package | What's scraped | How |
|---|---|---|
| bbe-networking | Traefik | PodMonitor, its pods' `metrics` port (9100). Its Service doesn't expose it |
| bbe-networking | cert-manager | ServiceMonitor, its Service's `http-metrics` port (9402) |
| bbe-networking | Blocky | ServiceMonitor, its Service's `http` port (4000). Blocky's own ServiceMonitor is off |
| bbe-storage | Longhorn's managers | ServiceMonitor, `longhorn-backend`'s `manager` port (9500) |
| bbe-auth | authentik's server | PodMonitor, its pods' `metrics` port (9300). Its chart's metrics Service is off |

Each package's monitors can be turned off under `bbe.observability.monitors`, for a cluster without it.

### 4. The control plane is found by Talos' labels

Talos runs the API server, controller manager and scheduler as static pods on the host network, labelled `k8s-app` (as Talos v1.14.2's `k8stemplates` set them), rather than kubeadm's `component`. kube-prometheus-stack's Services for them select those labels instead.

etcd isn't a pod on Talos. It runs on the control plane nodes themselves, where the API server's pods run on the host network. So etcd's Service selects the API server's pods, whose addresses are the control plane nodes', on etcd's metrics port 2381.

Talos serves none of these metrics on the node's address by default. bbe setup has new clusters serve them (bbe-quest#56), and its firewall keeps them, with node-exporter's 9100, to the trusted networks and pods:
- etcd on 2381;
- the controller manager on 10257 and the scheduler on 10259, both over HTTPS;
- kube-proxy on 10249.

On clusters set up before, these targets show as down in Prometheus, and kube-prometheus-stack's rules alert on them until the nodes' config is changed the same way.

### 5. Alertmanager's config is written from bbe.yaml

`bbe.observability.alerts.receiver` is one receiver in [Alertmanager's format](https://prometheus.io/docs/alerting/latest/configuration/#receiver), such as Telegram, email, ntfy through a webhook, or Discord. Without one, alerts go nowhere and are only shown in Grafana. bbe records it in `bbe.yaml` with its default, so it's there to fill in.

Credentials stay out of `bbe.yaml`. They go in the `bbe-observability-alerts` secret, mounted into Alertmanager, where its receivers read them from files (`bot_token_file`, `auth_password_file` and so on). The chart creates the secret empty, and keeps what's added to it, as bbe-auth keeps its generated passwords.

kube-prometheus-stack's Watchdog, which always fires to show alerting works, is never sent.

### 6. A few rules of bbe's own

kube-prometheus-stack's rules already alert on nodes going down, filesystems and volumes filling up, and pods crash looping. bbe adds what they don't know about:

| Alert | When |
|---|---|
| `LonghornVolumeDegraded` | A volume has fewer copies than it should, for 10 minutes |
| `LonghornVolumeFaulted` | A volume has no copy Longhorn can use |
| `LonghornDiskAlmostFull` | A Longhorn disk is more than 85% full (`bbe.observability.rules.longhornDiskUsagePercent`) |
| `LonghornNodeDown` | A Longhorn node isn't ready, for 10 minutes |
| `CertificateExpiringSoon` | A certificate expires within 14 days (`bbe.observability.rules.certificateExpiryDays`). cert-manager renews the domain's a third of the way before it expires, so one this close failed to renew |
| `CertificateNotReady` | cert-manager couldn't issue a certificate, for 30 minutes |

The Windows rules and dashboards, and the AIX and macOS node dashboards, are off.

### 7. Its pods may run as root and on the host

node-exporter reads each node's metrics from its network, processes and filesystem, and Alloy reads the pods' log files from the node's disk. `baseline` allows neither, so the package's namespace is `privileged` (`bbe/pod-security`), like bbe-media's.

The Prometheus operator's admission webhooks are off. They only check rules and monitors as they're made, and would need the API server to reach the operator, with jobs making certificates on every upgrade.

## Consequences

- **The package takes about 1.2Gi of memory, and up to 4Gi**, plus about 100Mi for each node added.
- **The metrics and logs are deleted with the package**, by `bbe uninstall`. The Prometheus operator's CRDs stay, as Helm never deletes CRDs.
- **The control plane's metrics need nodes set up by a bbe that serves them** (decision 4). Older clusters show those targets as down.
- **Alerts go nowhere until a receiver is set.**
- **Grafana trusts the username header it's given.** Anything reaching its pod directly, rather than through Traefik, could claim to be anyone. Its NetworkPolicy lets only Traefik in from outside the package ([0007](0007-network-policies.md)), which only clusters enforcing NetworkPolicies honour.
- **bbe-observability needs bbe 1.7.0**, for the prerequisites naming only a package, and the values it records.
- **Not verified on a cluster**, as there's no test cluster. The chart renders, its unit tests pass, and the control plane's labels were checked in Talos v1.14.2's source, and its ports follow Talos' and kube-prometheus-stack's documentation.
