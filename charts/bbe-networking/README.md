# bbe-networking

![Version: 0.3.1](https://img.shields.io/badge/Version-0.3.1-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square)

A collection of charts for BBE cluster networking

**Homepage:** <https://brains-beyond-expectations.github.io/bbe-charts>

## Requirements

| Repository | Name | Version |
|------------|------|---------|
| https://brains-beyond-expectations.github.io/bbe-charts | blocky | 1.2.0 |
| https://charts.jetstack.io | cert-manager | v1.21.2 |
| https://metallb.github.io/metallb | metallb | 0.14.9 |
| https://traefik.github.io/charts | traefik | 41.7.1 |

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| bbe.certificates.caDuration | string | `"87600h"` | How long bbe's certificate authority is valid. Devices that trust it need its new certificate once it's renewed |
| bbe.certificates.duration | string | `"2160h"` | How long the certificate for the domain is valid. cert-manager renews it a third of the way before it expires |
| bbe.dashboard.bookmarks | list | `[]` | Homepage's bookmarks.yaml |
| bbe.dashboard.enabled | bool | `true` | Whether to serve the cluster's landing page at https://<domain>, with Homepage. It lists every app whose Ingress has `gethomepage.dev/enabled: "true"`, with whether its pods run |
| bbe.dashboard.image.repository | string | `"ghcr.io/gethomepage/homepage"` | The Homepage image |
| bbe.dashboard.image.tag | string | `"v2.5.0"` | The Homepage version |
| bbe.dashboard.resources.limits.memory | string | `"256Mi"` | The memory to limit the dashboard to |
| bbe.dashboard.resources.requests.cpu | string | `"10m"` | The CPU to request for the dashboard |
| bbe.dashboard.resources.requests.memory | string | `"96Mi"` | The memory to request for the dashboard |
| bbe.dashboard.services | list | `[]` | Links to list besides the apps found in the cluster, as Homepage's services.yaml |
| bbe.dashboard.settings | string | `"title: bbe\nheaderStyle: clean\nlayout:\n  Watch:\n    style: row\n    columns: 4\n  Read:\n    style: row\n    columns: 4\n  Listen:\n    style: row\n    columns: 4\n  Keep:\n    style: row\n    columns: 4\n  Manage:\n    style: row\n    columns: 4\n  Cluster:\n    style: row\n    columns: 4\n"` | Homepage's settings.yaml, see https://gethomepage.dev/configs/settings. Its layout orders the groups the apps' annotations put them in, so it's kept as text, as Helm would sort the groups by name |
| bbe.dashboard.widgets | list | `[]` | Homepage's widgets.yaml. Its Kubernetes widgets need metrics-server, which Talos doesn't run by default |
| bbe.metallb.blocky.ipAddressPool | string | `nil` | The IP address for the Blocky DNS service, or a range such as 192.168.1.240-192.168.1.245 |
| blocky.config.yaml | string | `"upstream:\n  default:\n    - 1.1.1.1\n    - 8.8.8.8\ncustomDNS:\n  mapping:\n    {{ .Values.global.bbe.domain }}: {{ .Values.global.bbe.ingress.loadBalancerIP }}\nblocking:\n  blackLists:\n    ads:\n      - https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts\n  clientGroupsBlock:\n    default:\n      - ads\nport: 53\nhttpPort: 4000\ncaching:\n  minTime: 5m\n  maxTime: 30m\nprometheus:\n  enable: true\n"` |  |
| blocky.service.annotations."metallb.io/address-pool" | string | `"blocky"` |  |
| cert-manager.crds.enabled | bool | `false` |  |
| cert-manager.startupapicheck.jobAnnotations."helm.sh/hook" | string | `"post-install,post-upgrade"` |  |
| cert-manager.startupapicheck.jobAnnotations."helm.sh/hook-delete-policy" | string | `"before-hook-creation,hook-succeeded"` |  |
| cert-manager.startupapicheck.jobAnnotations."helm.sh/hook-weight" | string | `"1"` |  |
| cert-manager.startupapicheck.rbac.annotations."helm.sh/hook" | string | `"post-install,post-upgrade"` |  |
| cert-manager.startupapicheck.rbac.annotations."helm.sh/hook-delete-policy" | string | `"before-hook-creation,hook-succeeded"` |  |
| cert-manager.startupapicheck.rbac.annotations."helm.sh/hook-weight" | string | `"-5"` |  |
| cert-manager.startupapicheck.serviceAccount.annotations."helm.sh/hook" | string | `"post-install,post-upgrade"` |  |
| cert-manager.startupapicheck.serviceAccount.annotations."helm.sh/hook-delete-policy" | string | `"before-hook-creation,hook-succeeded"` |  |
| cert-manager.startupapicheck.serviceAccount.annotations."helm.sh/hook-weight" | string | `"-5"` |  |
| global.bbe.domain | string | `"bbe.home.arpa"` | The domain the cluster's apps are named under, such as jellyfin.bbe.home.arpa. Blocky answers for it and everything under it with the ingress's IP, and bbe's own certificate authority signs a certificate for it. home.arpa itself can't be used: browsers treat it as a public suffix like .com, so a certificate for *.home.arpa is refused and a login can't be shared between apps under it |
| global.bbe.ingress.loadBalancerIP | string | `nil` | The IP address for the ingress, on the same network as your nodes |
| metallb.crds.enabled | bool | `false` |  |
| metallb.crds.validationFailurePolicy | string | `"Ignore"` |  |
| metallb.speaker.ignoreExcludeLB | bool | `true` |  |
| traefik.ingressClass.enabled | bool | `true` |  |
| traefik.ingressClass.isDefaultClass | bool | `true` |  |
| traefik.ingressClass.name | string | `"traefik"` |  |
| traefik.ports.web.http.redirections.entryPoint.permanent | bool | `true` |  |
| traefik.ports.web.http.redirections.entryPoint.scheme | string | `"https"` |  |
| traefik.ports.web.http.redirections.entryPoint.to | string | `"websecure"` |  |
| traefik.providers.kubernetesIngress.publishedService.enabled | bool | `true` |  |
| traefik.service.annotations."metallb.io/address-pool" | string | `"default"` |  |
| traefik.service.type | string | `"LoadBalancer"` |  |
| traefik.tlsStore.default.defaultCertificate.secretName | string | `"bbe-domain-tls"` |  |

----------------------------------------------
Autogenerated from chart metadata using [helm-docs v1.14.2](https://github.com/norwoodj/helm-docs/releases/v1.14.2)
