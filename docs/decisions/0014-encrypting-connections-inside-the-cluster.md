# 0014: Encrypting connections inside the cluster

**Status:** proposed, 2026-11-13

## Context

Traefik ends people's HTTPS with the domain's certificate ([0002](0002-single-sign-on.md)). Behind it, the apps talked to each other, and Traefik to them, in plain HTTP and LDAP. Pods on different nodes reach each other through Flannel's VXLAN, across the house's network, unencrypted. Anyone on that network could read:
- **Every sign-in session.** Forward auth sends each request's authentik cookie to authentik's server.
- **People's passwords.** Jellyfin, the book library and Snipe-IT check them against authentik's LDAP outpost.
- **API keys and the apps' data**, between the Servarr apps, qBittorrent, Seerr and the rest.

NetworkPolicies ([0007](0007-network-policies.md)) limit who connects, not who can read the traffic. Calibre-Web-Automated already serves HTTPS itself behind Traefik ([0004](0004-book-library.md), decision 7).

**What each app can do**, from its source at the version bbe runs, checked on 2026-11-13:

| | Apps |
|---|---|
| **HTTPS on a port of its own, plain HTTP kept for probes** | Sonarr, Radarr, Prowlarr and Lidarr (a PKCS#12 file), Jellyfin (PKCS#12), slskd (PKCS#12), Snipe-IT (PEM files at fixed paths), authentik's server (on 9443) |
| **HTTPS instead of HTTP on its only port** | SoulSync and Shelfmark (through their gunicorn), Open WebUI (its uvicorn), Grafana, Prometheus, Alertmanager, Loki, qBittorrent (or the nginx in its pod) |
| **LDAPS** | authentik's LDAP outpost |
| **No TLS at all** | Bazarr, autobrr, Seerr, FlareSolverr, Homepage, Ollama, and the Wyoming speech servers |

**What they need to trust bbe's certificate authority, as clients:**
- **.NET and Go** read `SSL_CERT_FILE` on top of the system's roots, and **Node** reads `NODE_EXTRA_CA_CERTS`.
- **Python's requests and aiohttp**, and the variables Music Assistant and Open WebUI read, *replace* the public roots instead. Apps that also reach the internet then need one file with both.

**What reloads a renewed certificate:**
- **Without a restart:** authentik, Calibre-Web, SoulSync, Prometheus, Alertmanager, Loki, and Grafana (with `certs_watch_interval`).
- **Only when they start:** the rest.

## Decision

It's done in steps:
1. **The shared parts:** bbe's certificate authority in every namespace, and restarts on renewal.
2. **authentik:** its server and its LDAP outpost, which carry the sessions and the passwords.
3. **Next:** the apps serving HTTPS on a port of their own.
4. **Then:** the apps where HTTPS replaces their only port.

This records steps 1 and 2. Each app gets a certificate from the `bbe-ca` ClusterIssuer for its Service's names, as CWA's.

### 1. trust-manager copies bbe's certificate authority into every namespace

bbe-networking runs [trust-manager](https://cert-manager.io/docs/trust/trust-manager/), cert-manager's own, with two bundles:
- **`bbe-ca-cert`**, a Secret holding only bbe's certificate authority under `ca.crt`. It's for checking the apps' own certificates. Traefik's forward auth only reads its certificate authority from a Secret, in the middleware's own namespace.
- **`bbe-ca-bundle`**, a ConfigMap holding the public certificate authorities and bbe's under `ca-bundle.crt`. It's for the Python apps, which can only be given one file and reach the internet too.

trust-manager may only write the `bbe-ca-cert` Secret. To manage it in every namespace, it can read every Secret, as cert-manager can.

The bundles are hooks, like bbe's certificates. trust-manager's webhook checks them, and doesn't answer yet when the chart's resources are created. A hook Job waits for it first, as cert-manager's startup check does for cert-manager. Its CRD is in `crds/`, from `update-crds.sh`, so Helm knows it before then.

trust-manager's webhook certificate is issued by Helm, not cert-manager. cert-manager's webhook doesn't answer yet when trust-manager's Certificate would be created, on a first install.

Rejected:
- **A Helm `lookup` copying the certificate authority into each package.** It would go stale when the authority is renewed, until each package was upgraded.
- **Building a bundle in each pod with an init container.** It's more to repeat in every chart.

### 2. Reloader restarts what reads its certificate only when it starts

bbe-networking runs [Reloader](https://github.com/stakater/Reloader). A workload whose app only reads its certificate at start names its Secret in a `secret.reloader.stakater.com/reload` annotation. Reloader rolls it when cert-manager renews the certificate. Nothing needs it in step 2, as authentik reloads its own certificates. It's for step 3.

Rejected: **long-lived certificates instead.** They would still expire on a pod that never restarts.

### 3. authentik's server serves bbe's certificate

- **Its certificate:** `bbe-auth-server`, for its Service, mounted on the worker at `/certs/bbe-auth-server`.
- **How it gets into authentik:** the worker imports what's in `/certs` as keypairs named after their folders. It does that when a file changes and once an hour, and again when cert-manager renews the certificate, into the same keypair. The worker can read the key through its group only.
- **How it's served:** the setup has the default brand serve that keypair on 9443. authentik's server looks for a changed certificate every 3 minutes.
- **Traefik** reaches authentik on 9443 with a ServersTransport trusting `bbe-ca-cert`, for `bbe-auth-server.bbe-auth.svc`. This covers the sign-in pages and the book library's sign-in callback.
- **Forward auth**, in bbe-media, bbe-library, bbe-music and bbe-observability, asks `https://bbe-auth-server.bbe-auth.svc.cluster.local` with `tls.caSecret: bbe-ca-cert`.
- **qBittorrent's nginx** asks over HTTPS too, with `proxy_ssl_verify`.
- **The LDAP outpost** reaches authentik over HTTPS, trusting only `bbe-ca-cert` (`SSL_CERT_FILE`). `AUTHENTIK_INSECURE` is gone.

**How the setup has authentik serve it:**
1. **Import.** It asks authentik to import `/certs` now. Its API runs the import's schedule.
2. **Wait.** It waits until the imported keypair's fingerprint is the certificate's. It reads that certificate, without its key, from the Secret.
3. **Serve.** It sets the keypair on the default brand, and the LDAP certificate on the LDAP provider.

On a first install, authentik serves its own self-signed certificate until then. So the setup talks to it in plain HTTP inside the namespace, but only to apply the blueprint and do the three steps above. Then it waits until authentik serves bbe's certificate, and only then sends the outpost's token and people's passwords, over HTTPS. The setup uses HTTPS from the start when authentik already serves it, which is on every upgrade.

Rejected:
- **Uploading the keypair through the API.** It would send the key over the network, and the worker's import would make a second keypair of the same name.
- **Naming the certificate in the blueprint** (`!Find`). The worker applies the blueprint when it starts, before anything has imported the certificate, and doesn't apply it again unless the blueprint changes.

### 4. The LDAP outpost only serves LDAPS outside its pod

- **The outpost:** `bbe-auth-ldap` gets a certificate for its Service, imported the same way and set on the LDAP provider. Its Service and NetworkPolicy only offer LDAPS, on 636. Plain LDAP stays inside the pod, for its probe.
- **Jellyfin:** its LDAP plugin uses LDAPS, checking with `LdapRootCaPath`, bbe's certificate authority mounted in Jellyfin's pod. The plugin refuses a certificate that doesn't name the server.
- **The book library:** CWA uses LDAPS, but only checks the certificate when it's given a client certificate too, so it gets its own ([0004](0004-book-library.md)). The setup and the people CronJob check with python-ldap and bbe's certificate authority.
- **Snipe-IT:** connects to `ldaps://…:636`, with `LDAPTLS_CACERT` naming bbe's certificate authority. It still refuses a certificate it can't check (`ldap_server_cert_ignore` stays off).

### 5. What stays in plain HTTP

These apps can't serve TLS, and stay in plain HTTP behind their NetworkPolicies:
- Bazarr, autobrr, Seerr and FlareSolverr;
- Homepage, which also doesn't check the certificates of the apps it reads;
- Ollama, and the Wyoming speech servers, which Home Assistant reaches from outside the cluster.

Adding a TLS sidecar to each would be a lot to maintain for what they carry.

Music Assistant stays in plain HTTP too. Its Android apps connect to it on the LAN in plain HTTP, as they don't trust a certificate authority the user installs.

PostgreSQL and MariaDB are left for later. They can serve TLS, but only reload a certificate when asked to.

## Consequences

- **Upgrade bbe-networking first.** Every package now mounts or names `bbe-ca-cert`, which only exists once trust-manager runs. A pod naming it waits until it's there.
- **Upgrade bbe-auth, then the packages signing people in with LDAP.** Plain LDAP is no longer offered outside the outpost's pod. Jellyfin, the library and Snipe-IT can't sign people in from the moment bbe-auth is upgraded until their own package is.
- **A first install takes up to about 3 minutes longer,** while authentik picks up its certificate.
- **The setup sends authentik's bootstrap token in plain HTTP inside bbe-auth's namespace, on a first install only,** until authentik serves bbe's certificate. It sends nothing else secret that way.
- **trust-manager can read every Secret**, to manage `bbe-ca-cert` in every namespace.
- **Upgrading bbe-networking recreates the bundles,** and trust-manager writes their copies again within seconds. Pods already running keep the copy they have. Forward auth may fail for those seconds, while its Secret is being written again.
- **trust-manager's webhook certificate** is issued by Helm for 10 years, and again on every upgrade.
- **Not verified on a cluster yet.** The charts render and their unit tests pass. The setup's steps follow authentik 2026.8.4's API schema and source, and the clients' TLS settings their source at the versions bbe runs.
