# 0007: NetworkPolicies, and a firewall on the nodes

**Status:** proposed, 2026-10-22

## Context

Any pod could reach any app directly, around the sign-in. [0002](0002-single-sign-on.md) (decision 7) left two gaps open because Talos' Flannel doesn't enforce NetworkPolicy:
- the Servarr apps' `/initialize.json` hands their API key to any pod that asks;
- qBittorrent's own port can't be fenced off.

The nodes had the same problem one level down. The Talos API, the Kubernetes API, etcd, the kubelet and Flannel's VXLAN port answered anyone on the home network, the guest Wi-Fi included when it isn't separated.

The goal is for each app to be reached only by what uses it, and the cluster's own ports only by the computers managing it, without changing how anything is installed or reached.

## Decisions

### 1. Talos' Flannel enforces them, with kube-network-policies

`bbe setup` sets `KubeFlannelCNIConfig.kubeNetworkPoliciesEnabled` on the clusters it creates (bbe-quest#56). Talos, since 1.13, then runs [kube-network-policies](https://github.com/kubernetes-sigs/kube-network-policies) as a second container of Flannel's DaemonSet.

It sends new connections to and from pods through NFQUEUE, in the nodes' `postrouting` hook, and decides on them in userspace. Three things follow from how it works:
- **Traffic the node sends as root isn't checked**, so the kubelet's probes always get through.
- **Traffic from the node's network that isn't root is checked, as coming from the node's address.** That covers the API server, which Talos runs as `nobody`, and pods on the host network such as Music Assistant. No pod or namespace selector matches it, so a pod the API server calls must not be selected by any policy. That rules out admission webhooks and metrics-server's APIService.
- **It fails open**: while its controller isn't running, connections go through (`--fail-open`, on by default).

Rejected: **Cilium**, which would also show the flows (Hubble) and filter on HTTP. Talos would run no CNI and no kube-proxy, and bbe would install Cilium with Helm between the bootstrap and the health check, and upgrade it from then on. Existing clusters would need a CNI migration. kube-network-policies is one switch in the config Talos already manages.

### 2. Each package fences off its own apps, for traffic coming in

Each package chart has `templates/network-policy.yaml`, on by default (`bbe.networkPolicy.enabled`):

| Package | Pods | Who may reach them |
|---|---|---|
| bbe-media | all | its own pods, and Traefik |
| | Prowlarr | also bbe-music and bbe-library |
| | qBittorrent, its own port only, not its nginx | also bbe-music and bbe-library |
| | FlareSolverr | also bbe-library |
| bbe-music | all | its own pods, and Traefik |
| | Lidarr | also bbe-media's Prowlarr |
| | slskd's Soulseek port, without the VPN | anyone, as the router forwards it there |
| bbe-library | all | its own pods, and Traefik |
| bbe-misc | all | its own pods |
| | Snipe-IT | also Traefik |
| bbe-auth | all | its own pods |
| | authentik's server, its `http` port | also Traefik, bbe-media (qBittorrent's nginx) and bbe-library (Shelfmark) |
| | authentik's server, its `metrics` port | also bbe-observability |
| | the LDAP outpost | also bbe-media (Jellyfin), bbe-library and bbe-misc (Snipe-IT) |
| bbe-observability | all but metrics-server | its own pods |
| | Grafana | also Traefik, as Grafana trusts the user named in a header that only Traefik may send ([0006](0006-observability.md)) |

How the policies are written:
- **Traefik is its pods only.** The policies match the `bbe-networking` namespace and Traefik's `app.kubernetes.io/name: traefik`, not Homepage or Blocky beside it.
- **Namespaces are matched by `kubernetes.io/metadata.name`.** That's the package's name, as the charts already name each other's services by namespace.
- **Ports are matched by name**, on the pod's own ports, not the Service's: `http`, `ldap`, `metrics`, `grafana`, `soulseek`.
- **Policies add up.** A pod accepts what any policy selecting it allows, so each package has one policy for its own pods and Traefik, and one per app other packages call.

Only traffic coming in is limited. The apps reach the internet for indexers, metadata and the VPN, and a list of where they may go would break with every indexer added.

Every selector and named port was checked against the charts rendered together: each matches pods, and each port exists on the pods it's meant for.

### 3. What the policies leave out

- **bbe-networking and bbe-storage have none.** The API server calls cert-manager's and MetalLB's webhooks and Longhorn's, from the node's network (decision 1). Traefik and Blocky are reached from the whole network anyway.
- **Pods on the host network aren't covered:** Music Assistant, and bbe-observability's node-exporter. Their ports are the node's own.
- **Traffic going out** isn't limited (decision 2).

### 4. The nodes' firewall keeps the cluster's own ports to the trusted networks

`bbe setup` asks which networks may reach the Talos and Kubernetes APIs, suggesting the node's `/24`, and adds a Talos `NetworkRuleConfig` for each group of ports (bbe-quest#56):

| Ports | What | Who may connect |
|---|---|---|
| 50000, 50001 | The Talos API, and the control plane handing out certificates | the trusted networks |
| 2379-2380 | etcd | the trusted networks |
| 6443 | The Kubernetes API | the trusted networks, and pods, which reach it at the node's address through its Service |
| 10250 | The kubelet | the trusted networks, and pods: metrics-server and Prometheus |
| 2381, 9100, 10249, 10257, 10259 | Metrics: etcd, node-exporter, kube-proxy, the controller manager and the scheduler | the trusted networks, and pods: Prometheus |
| 4789/udp | Flannel's VXLAN | the trusted networks |

The firewall's default action stays `accept`. Talos then drops new connections to a rule's ports from outside its subnets, and leaves every other port open, so Traefik, Blocky, MetalLB and Music Assistant are reached as before.

The trusted networks have to hold every node and the computers managing the cluster. bbe asks again when they leave out the node, or the address the computer running bbe reaches it from, which would lock bbe out of the node it's setting up.

## Consequences

- **0002's gaps are closed** where NetworkPolicies are enforced. A Servarr app's API key and qBittorrent's port are only reached from bbe-media itself and the packages listed. A pod in bbe-media can still reach every app in it.
- **A package calling another's app has to be added to that app's policy.** Until it is, its connections hang and time out.
- **Clusters created before bbe-quest#56 don't enforce the policies**, which are installed but do nothing. Turning enforcement on, and the firewall, means applying the same Talos documents to their nodes (bbe-quest's README).
- **Moving the computer managing the cluster to another network locks it out**, until a computer on a trusted network changes the nodes' firewall.
- **Not verified on a cluster**, as there's no test cluster:
  - The policies render, their unit tests pass, and every selector and named port matches the rendered pods.
  - Both Talos configs validate with talosctl v1.14.2.
  - How enforcement and the firewall behave was read from the source of kube-network-policies and Talos v1.14.2, not watched.
