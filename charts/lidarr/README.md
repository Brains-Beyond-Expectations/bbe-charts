# lidarr

![Version: 0.0.1](https://img.shields.io/badge/Version-0.0.1-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: 3.1.0](https://img.shields.io/badge/AppVersion-3.1.0-informational?style=flat-square)

Lidarr is a music collection manager for Usenet and BitTorrent users. It monitors artists and albums, and grabs, sorts and renames new releases.

**Homepage:** <https://brains-beyond-expectations.github.io/bbe-charts>

## Source Code

* <https://github.com/Lidarr/Lidarr>

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| config.accessMode | string | `"ReadWriteOnce"` | The access mode to use for the Lidarr config persistent volume claim |
| config.annotations | object | `{}` | Annotations to apply to the Lidarr config persistent volume claim |
| config.enabled | bool | `true` | Whether to enable the creation of a persistent volume claim for the Lidarr config |
| config.existingClaim | string | `""` | Use this attribute to reference an existing persistent volume claim to use for the Lidarr config |
| config.retain | bool | `false` | Whether to keep the persistent volume claim for the config after the Lidarr chart is uninstalled |
| config.size | string | `"1Gi"` | The amount of storage to request for the Lidarr config |
| config.storageClass | string | `""` | Storage class to use for the Lidarr config persistent volume claim |
| fullnameOverride | string | `""` | Optional full name override for the resources |
| ingress.annotations | object | `{}` | Annotations to apply to the Lidarr ingress |
| ingress.enabled | bool | `false` | Whether to create an ingress for Lidarr |
| ingress.hosts | list | `[]` | Host configuration for the Lidarr ingress |
| ingress.ingressClassName | string | `""` | The ingress class to use for the Lidarr ingress |
| ingress.mainPort | int | `8686` | The main http port to use for the Lidarr ingress |
| ingress.tls | list | `[]` | TLS configuration for the Lidarr ingress |
| lidarr.annotations | object | `{}` | Annotations to apply to the Lidarr pod |
| lidarr.env | list | `[]` | The environment variables to set for the Lidarr pod |
| lidarr.image.repository | string | `"lscr.io/linuxserver/lidarr"` | The image repository to pull from |
| lidarr.image.tag | string | `""` | The image tag to pull |
| lidarr.livenessProbe | object | `{"failureThreshold":5,"httpGet":{"path":"/ping","port":8686},"initialDelaySeconds":60,"periodSeconds":10,"successThreshold":1,"timeoutSeconds":10}` | The livenessProbe configuration for the Lidarr pod |
| lidarr.readinessProbe | object | `{"failureThreshold":3,"httpGet":{"path":"/ping","port":8686},"initialDelaySeconds":0,"periodSeconds":10,"timeoutSeconds":1}` | The readinessProbe configuration for the Lidarr pod |
| lidarr.replicas | int | `1` | How many replicas of the Lidarr pod to run |
| lidarr.resources.limits.cpu | string | `""` | The amount of CPU to limit the Lidarr pod to |
| lidarr.resources.limits.memory | string | `"512Mi"` | The amount of memory to limit the Lidarr pod to |
| lidarr.resources.requests.cpu | string | `"50m"` | The amount of CPU to request for the Lidarr pod |
| lidarr.resources.requests.memory | string | `"512Mi"` | The amount of memory to request for the Lidarr pod |
| lidarr.securityContext.readOnlyRootFilesystem | bool | `false` | Whether to run Lidarr with a read-only root filesystem |
| lidarr.securityContext.runAsGroup | int | `0` | The group ID to run Prowlarr as |
| lidarr.securityContext.runAsUser | int | `0` | The user ID to run Lidarr as |
| lidarr.startupProbe | object | `{"failureThreshold":30,"httpGet":{"path":"/ping","port":8686},"initialDelaySeconds":0,"periodSeconds":5,"timeoutSeconds":1}` | The startupProbe configuration for the Lidarr pod |
| lidarr.strategyType | string | `"Recreate"` | The strategy to use for updating the Lidarr pods |
| media.accessMode | string | `"ReadWriteOnce"` | The access mode to use for the Lidarr media persistent volume claim |
| media.annotations | object | `{}` | Annotations to apply to the Lidarr media persistent volume claim |
| media.enabled | bool | `true` | Whether to enable the creation of a persistent volume claim for the Lidarr media |
| media.existingClaim | string | `""` | Use this attribute to reference an existing persistent volume claim to use for the Lidarr media |
| media.retain | bool | `false` | Whether to keep the persistent volume claim for the media after the Lidarr chart is uninstalled |
| media.size | string | `"50Gi"` | The amount of storage to request for the Lidarr media |
| nameOverride | string | `""` | Optional short name override for the resources |
| namespaceOverride | string | `""` | Optional namespace override for the resources |
| service.annotations | object | `{}` | Annotations to apply to the Lidarr service |
| service.ports | list | `[{"name":"http","port":8686,"protocol":"TCP"}]` | Port to expose the Lidarr service on |
| service.type | string | `"ClusterIP"` | The type of service to create |

----------------------------------------------
Autogenerated from chart metadata using [helm-docs v1.14.2](https://github.com/norwoodj/helm-docs/releases/v1.14.2)
