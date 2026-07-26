# qbittorrent

![Version: 0.0.3](https://img.shields.io/badge/Version-0.0.3-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: 5.2.3](https://img.shields.io/badge/AppVersion-5.2.3-informational?style=flat-square)

qBittorrent is a BitTorrent client programmed in C++ / Qt that uses libtorrent

**Homepage:** <https://brains-beyond-expectations.github.io/bbe-charts>

## Source Code

* <https://github.com/qbittorrent/qbittorrent>

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| config.accessMode | string | `"ReadWriteOnce"` | The access mode to use for the qBittorrent config persistent volume claim |
| config.annotations | object | `{}` | Annotations to apply to the qBittorrent config persistent volume claim |
| config.enabled | bool | `true` | Whether to enable the creation of a persistent volume claim for the qBittorrent config |
| config.existingClaim | string | `""` | Use this attribute to reference an existing persistent volume claim to use for the qBittorrent config |
| config.retain | bool | `false` | Whether to keep the persistent volume claim for the config after the qBittorrent chart is uninstalled |
| config.size | string | `"1Gi"` | The amount of storage to request for the qBittorrent config |
| config.storageClass | string | `""` | Storage class to use for the qBittorrent config persistent volume claim |
| fullnameOverride | string | `""` | Optional full name override for the resources |
| ingress.annotations | object | `{}` | Annotations to apply to the qBittorrent ingress |
| ingress.enabled | bool | `false` | Whether to create an ingress for qBittorrent |
| ingress.hosts | list | `[]` | Host configuration for the qBittorrent ingress |
| ingress.ingressClassName | string | `""` | The ingress class to use for the qBittorrent ingress |
| ingress.mainPort | int | `8080` | The main http port to use for the qBittorrent ingress |
| ingress.tls | list | `[]` | TLS configuration for the qBittorrent ingress |
| media.accessMode | string | `"ReadWriteOnce"` | The access mode to use for the qBittorrent media persistent volume claim |
| media.annotations | object | `{}` | Annotations to apply to the qBittorrent media persistent volume claim |
| media.enabled | bool | `true` | Whether to enable the creation of a persistent volume claim for the qBittorrent media |
| media.existingClaim | string | `""` | Use this attribute to reference an existing persistent volume claim to use for the qBittorrent media |
| media.retain | bool | `false` | Whether to keep the persistent volume claim for the media after the qBittorrent chart is uninstalled |
| media.size | string | `"50Gi"` | The amount of storage to request for the qBittorrent media |
| nameOverride | string | `""` | Optional short name override for the resources |
| namespaceOverride | string | `""` | Optional namespace override for the resources |
| qbittorrent.annotations | object | `{}` | Annotations to apply to the qBittorrent pod |
| qbittorrent.env | list | `[]` | The environment variables to set for the qBittorrent pod |
| qbittorrent.image.repository | string | `"ghcr.io/linuxserver/qbittorrent"` | The image repository to pull from |
| qbittorrent.image.tag | string | `""` | The image tag to pull |
| qbittorrent.livenessProbe | object | `{"failureThreshold":5,"initialDelaySeconds":0,"periodSeconds":10,"successThreshold":1,"tcpSocket":{"port":8080},"timeoutSeconds":10}` | The livenessProbe configuration for the qBittorrent pod |
| qbittorrent.readinessProbe | object | `{"failureThreshold":3,"initialDelaySeconds":0,"periodSeconds":10,"tcpSocket":{"port":8080},"timeoutSeconds":1}` | The readinessProbe configuration for the qBittorrent pod |
| qbittorrent.replicas | int | `1` | How many replicas of the qBittorrent pod to run |
| qbittorrent.resources.limits.cpu | string | `""` | The amount of CPU to limit the qBittorrent pod to |
| qbittorrent.resources.limits.memory | string | `"512Mi"` | The amount of memory to limit the qBittorrent pod to |
| qbittorrent.resources.requests.cpu | string | `"50m"` | The amount of CPU to request for the qBittorrent pod |
| qbittorrent.resources.requests.memory | string | `"512Mi"` | The amount of memory to request for the qBittorrent pod |
| qbittorrent.securityContext.readOnlyRootFilesystem | bool | `false` | Whether to run qBittorrent with a read-only root filesystem |
| qbittorrent.securityContext.runAsGroup | int | `0` | The group ID to run Prowlarr as |
| qbittorrent.securityContext.runAsUser | int | `0` | The user ID to run qBittorrent as |
| qbittorrent.startupProbe | object | `{"failureThreshold":30,"initialDelaySeconds":0,"periodSeconds":5,"tcpSocket":{"port":8080},"timeoutSeconds":1}` | The startupProbe configuration for the qBittorrent pod |
| qbittorrent.strategyType | string | `"Recreate"` | The strategy to use for updating the qBittorrent pods |
| service.annotations | object | `{}` | Annotations to apply to the qBittorrent service |
| service.ports | list | `[{"name":"http","port":8080,"protocol":"TCP"}]` | Port to expose the qBittorrent service on |
| service.type | string | `"ClusterIP"` | The type of service to create |
| wireguard.enabled | bool | `false` | Whether to run qBittorrent behind a WireGuard sidecar |
| wireguard.image.repository | string | `"lscr.io/linuxserver/wireguard"` | The image repository for the WireGuard sidecar |
| wireguard.image.tag | string | `"latest"` | The image tag for the WireGuard sidecar |
| wireguard.initContainer.image.repository | string | `"busybox"` | The image repository for the WireGuard network initialization container |
| wireguard.initContainer.image.tag | string | `"1.32.0"` | The image tag for the WireGuard network initialization container |
| wireguard.secret.key | string | `"wireguard-config"` | Key in the WireGuard Secret containing the configuration file |
| wireguard.secret.mountPath | string | `"/config/wg_confs"` | Mount path for the WireGuard configuration file |
| wireguard.secret.name | string | `""` | Name of the existing Secret containing the WireGuard configuration |

----------------------------------------------
Autogenerated from chart metadata using [helm-docs v1.14.2](https://github.com/norwoodj/helm-docs/releases/v1.14.2)
