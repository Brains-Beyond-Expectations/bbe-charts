# sonarr

![Version: 0.1.3](https://img.shields.io/badge/Version-0.1.3-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: 4.0.15](https://img.shields.io/badge/AppVersion-4.0.15-informational?style=flat-square)

Sonarr is a PVR for Usenet and BitTorrent users. It can monitor multiple RSS feeds for new episodes of your favorite shows and will grab, sort and rename them.

**Homepage:** <https://brains-beyond-expectations.github.io/bbe-charts>

## Source Code

* <https://github.com/Sonarr/Sonarr>

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| config.accessMode | string | `"ReadWriteOnce"` | The access mode to use for the Sonarr config persistent volume claim |
| config.annotations | object | `{}` | Annotations to apply to the Sonarr config persistent volume claim |
| config.enabled | bool | `true` | Whether to enable the creation of a persistent volume claim for the Sonarr config |
| config.existingClaim | string | `""` | Use this attribute to reference an existing persistent volume claim to use for the Sonarr config |
| config.retain | bool | `false` | Whether to keep the persistent volume claim for the config after the Sonarr chart is uninstalled |
| config.size | string | `"1Gi"` | The amount of storage to request for the Sonarr config |
| fullnameOverride | string | `""` | Optional full name override for the resources |
| ingress.annotations | object | `{}` | Annotations to apply to the Sonarr ingress |
| ingress.enabled | bool | `false` | Whether to create an ingress for Sonarr |
| ingress.hosts | list | `[]` | Host configuration for the Sonarr ingress |
| ingress.ingressClassName | string | `""` | The ingress class to use for the Sonarr ingress |
| ingress.mainPort | int | `8989` | The main http port to use for the Sonarr ingress |
| ingress.tls | list | `[]` | TLS configuration for the Sonarr ingress |
| media.accessMode | string | `"ReadWriteOnce"` | The access mode to use for the Sonarr media persistent volume claim |
| media.annotations | object | `{}` | Annotations to apply to the Sonarr media persistent volume claim |
| media.enabled | bool | `true` | Whether to enable the creation of a persistent volume claim for the Sonarr media |
| media.existingClaim | string | `""` | Use this attribute to reference an existing persistent volume claim to use for the Sonarr media |
| media.retain | bool | `false` | Whether to keep the persistent volume claim for the media after the Sonarr chart is uninstalled |
| media.size | string | `"50Gi"` | The amount of storage to request for the Sonarr media |
| nameOverride | string | `""` | Optional short name override for the resources |
| namespaceOverride | string | `""` | Optional namespace override for the resources |
| service.annotations | object | `{}` | Annotations to apply to the Sonarr service |
| service.ports | list | `[{"name":"http","port":8989,"protocol":"TCP"}]` | Port to expose the Sonarr service on |
| service.type | string | `"ClusterIP"` | The type of service to create |
| sonarr.annotations | object | `{}` | Annotations to apply to the Sonarr pod |
| sonarr.env | list | `[]` | The environment variables to set for the Sonarr pod |
| sonarr.image.repository | string | `"lscr.io/linuxserver/sonarr"` | The image repository to pull from |
| sonarr.image.tag | string | `""` | The image tag to pull |
| sonarr.livenessProbe | object | `{"exec":{"command":["/usr/bin/env","bash","-c","curl --fail localhost:8989/api/v3/system/status?apiKey=`IFS=\\> && while read -d \\< E C; do if [[ $E = \"ApiKey\" ]]; then echo $C; fi; done < /config/config.xml`"]},"failureThreshold":5,"initialDelaySeconds":60,"periodSeconds":10,"successThreshold":1,"timeoutSeconds":10}` | The livenessProbe configuration for the Sonarr pod |
| sonarr.readinessProbe | object | `{"failureThreshold":3,"initialDelaySeconds":0,"periodSeconds":10,"tcpSocket":{"port":8989},"timeoutSeconds":1}` | The readinessProbe configuration for the Sonarr pod |
| sonarr.replicas | int | `1` | How many replicas of the Sonarr pod to run |
| sonarr.resources.limits.cpu | string | `""` | The amount of CPU to limit the Sonarr pod to |
| sonarr.resources.limits.memory | string | `"512Mi"` | The amount of memory to limit the Sonarr pod to |
| sonarr.resources.requests.cpu | string | `"50m"` | The amount of CPU to request for the Sonarr pod |
| sonarr.resources.requests.memory | string | `"512Mi"` | The amount of memory to request for the Sonarr pod |
| sonarr.securityContext.readOnlyRootFilesystem | bool | `false` | Whether to run Sonarr with a read-only root filesystem |
| sonarr.securityContext.runAsGroup | int | `0` | The group ID to run Prowlarr as |
| sonarr.securityContext.runAsUser | int | `0` | The user ID to run Sonarr as |
| sonarr.startupProbe | object | `{"failureThreshold":30,"initialDelaySeconds":0,"periodSeconds":5,"tcpSocket":{"port":8989},"timeoutSeconds":1}` | The startupProbe configuration for the Sonarr pod |
| sonarr.strategyType | string | `"Recreate"` | The strategy to use for updating the Sonarr pods |

----------------------------------------------
Autogenerated from chart metadata using [helm-docs v1.14.2](https://github.com/norwoodj/helm-docs/releases/v1.14.2)
