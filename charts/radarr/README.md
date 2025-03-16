# radarr

![Version: 0.1.0](https://img.shields.io/badge/Version-0.1.0-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: 5.19.3](https://img.shields.io/badge/AppVersion-5.19.3-informational?style=flat-square)

Radarr is a movie collection manager for Usenet and BitTorrent users. It can monitor multiple RSS feeds for new movies and will interface with clients and indexers to grab, sort, and rename them.

**Homepage:** <https://brains-beyond-expectations.github.io/bbe-charts>

## Source Code

* <https://github.com/Radarr/Radarr>

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| config.accessMode | string | `"ReadWriteOnce"` | The access mode to use for the Radarr config persistent volume claim |
| config.annotations | object | `{}` | Annotations to apply to the Radarr config persistent volume claim |
| config.enabled | bool | `true` | Whether to enable the creation of a persistent volume claim for the Radarr config |
| config.existingClaim | string | `""` | Use this attribute to reference an existing persistent volume claim to use for the Radarr config |
| config.retain | bool | `false` | Whether to keep the persistent volume claim for the config after the Radarr chart is uninstalled |
| config.size | string | `"1Gi"` | The amount of storage to request for the Radarr config |
| fullnameOverride | string | `""` | Optional full name override for the resources |
| ingress.annotations | object | `{}` | Annotations to apply to the Radarr ingress |
| ingress.enabled | bool | `false` | Whether to create an ingress for Radarr |
| ingress.hosts | list | `[]` | Host configuration for the Radarr ingress |
| ingress.ingressClassName | string | `""` | The ingress class to use for the Radarr ingress |
| ingress.tls | list | `[]` | TLS configuration for the Radarr ingress |
| media.accessMode | string | `"ReadWriteOnce"` | The access mode to use for the Radarr media persistent volume claim |
| media.annotations | object | `{}` | Annotations to apply to the Radarr media persistent volume claim |
| media.enabled | bool | `true` | Whether to enable the creation of a persistent volume claim for the Radarr media |
| media.existingClaim | string | `""` | Use this attribute to reference an existing persistent volume claim to use for the Radarr media |
| media.retain | bool | `false` | Whether to keep the persistent volume claim for the media after the Radarr chart is uninstalled |
| media.size | string | `"50Gi"` | The amount of storage to request for the Radarr media |
| nameOverride | string | `""` | Optional short name override for the resources |
| namespaceOverride | string | `""` | Optional namespace override for the resources |
| radarr.annotations | object | `{}` | Annotations to apply to the Radarr pod |
| radarr.env | list | `[]` | The environment variables to set for the Radarr pod |
| radarr.image.repository | string | `"lscr.io/linuxserver/radarr"` | The image repository to pull from |
| radarr.image.tag | string | `""` | The image tag to pull |
| radarr.livenessProbe | object | `{"exec":{"command":["/usr/bin/env","bash","-c","curl --fail localhost:7878/api/v3/system/status?apiKey=`IFS=\\> && while read -d \\< E C; do if [[ $E = \"ApiKey\" ]]; then echo $C; fi; done < /config/config.xml`"]},"failureThreshold":5,"initialDelaySeconds":60,"periodSeconds":10,"successThreshold":1,"timeoutSeconds":10}` | The livenessProbe configuration for the Radarr pod |
| radarr.readinessProbe | object | `{"failureThreshold":3,"initialDelaySeconds":0,"periodSeconds":10,"tcpSocket":{"port":7878},"timeoutSeconds":1}` | The readinessProbe configuration for the Radarr pod |
| radarr.replicas | int | `1` | How many replicas of the Radarr pod to run |
| radarr.resources.limits.cpu | string | `""` | The amount of CPU to limit the Radarr pod to |
| radarr.resources.limits.memory | string | `"256Mi"` | The amount of memory to limit the Radarr pod to |
| radarr.resources.requests.cpu | string | `"100m"` | The amount of CPU to request for the Radarr pod |
| radarr.resources.requests.memory | string | `"256Mi"` | The amount of memory to request for the Radarr pod |
| radarr.securityContext.readOnlyRootFilesystem | bool | `false` | Whether to run Radarr with a read-only root filesystem |
| radarr.securityContext.runAsGroup | int | `0` | The group ID to run Prowlarr as |
| radarr.securityContext.runAsUser | int | `0` | The user ID to run Radarr as |
| radarr.startupProbe | object | `{"failureThreshold":30,"initialDelaySeconds":0,"periodSeconds":5,"tcpSocket":{"port":7878},"timeoutSeconds":1}` | The startupProbe configuration for the Radarr pod |
| radarr.strategyType | string | `"Recreate"` | The strategy to use for updating the Radarr pods |
| service.annotations | object | `{}` | Annotations to apply to the Radarr service |
| service.ports | list | `[{"name":"http","port":7878,"protocol":"TCP"}]` | Port to expose the Radarr service on |
| service.type | string | `"ClusterIP"` | The type of service to create |

----------------------------------------------
Autogenerated from chart metadata using [helm-docs v1.14.2](https://github.com/norwoodj/helm-docs/releases/v1.14.2)
