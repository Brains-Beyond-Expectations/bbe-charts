# bazarr

![Version: 0.1.1](https://img.shields.io/badge/Version-0.1.1-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: release-1.5.0](https://img.shields.io/badge/AppVersion-release--1.5.0-informational?style=flat-square)

Bazarr is a companion application to Sonarr and Radarr. It manages and downloads subtitles based on your requirements.

**Homepage:** <https://brains-beyond-expectations.github.io/bbe-charts>

## Source Code

* <https://github.com/morpheus65535/bazarr>

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| bazarr.annotations | object | `{}` | Annotations to apply to the Bazarr pod |
| bazarr.env | list | `[]` | The environment variables to set for the Bazarr pod |
| bazarr.image.repository | string | `"ghcr.io/hotio/bazarr"` | The image repository to pull from |
| bazarr.image.tag | string | `""` | The image tag to pull |
| bazarr.livenessProbe | object | `{"failureThreshold":3,"periodSeconds":10,"successThreshold":1,"tcpSocket":{"port":6767},"timeoutSeconds":1}` | The livenessProbe configuration for the Bazarr pod |
| bazarr.readinessProbe | object | `{"failureThreshold":3,"periodSeconds":10,"successThreshold":1,"tcpSocket":{"port":6767},"timeoutSeconds":1}` | The readinessProbe configuration for the Bazarr pod |
| bazarr.replicas | int | `1` | How many replicas of the Bazarr pod to run |
| bazarr.resources.limits.cpu | string | `""` | The amount of CPU to limit the Bazarr pod to |
| bazarr.resources.limits.memory | string | `"512Mi"` | The amount of memory to limit the Bazarr pod to |
| bazarr.resources.requests.cpu | string | `"50m"` | The amount of CPU to request for the Bazarr pod |
| bazarr.resources.requests.memory | string | `"512Mi"` | The amount of memory to request for the Bazarr pod |
| bazarr.securityContext.readOnlyRootFilesystem | bool | `false` | Whether to run Bazarr with a read-only root filesystem |
| bazarr.securityContext.runAsGroup | int | `0` | The group ID to run Bazarr as |
| bazarr.securityContext.runAsUser | int | `0` | The user ID to run Bazarr as |
| bazarr.startupProbe | object | `{"failureThreshold":30,"periodSeconds":5,"successThreshold":1,"tcpSocket":{"port":6767},"timeoutSeconds":1}` | The startupProbe configuration for the Bazarr pod |
| bazarr.strategyType | string | `"Recreate"` | The strategy to use for updating the Bazarr pods |
| config.accessMode | string | `"ReadWriteOnce"` | The access mode to use for the Bazarr config persistent volume claim |
| config.annotations | object | `{}` | Annotations to apply to the Bazarr config persistent volume claim |
| config.enabled | bool | `true` | Whether to enable the creation of a persistent volume claim for the Bazarr config |
| config.existingClaim | string | `""` | Use this attribute to reference an existing persistent volume claim to use for the Bazarr config |
| config.retain | bool | `false` | Whether to keep the persistent volume claim for the config after the Bazarr chart is uninstalled |
| config.size | string | `"1Gi"` | The amount of storage to request for the Bazarr config |
| fullnameOverride | string | `""` | Optional full name override for the resources |
| ingress.annotations | object | `{}` | Annotations to apply to the Bazarr ingress |
| ingress.enabled | bool | `false` | Whether to create an ingress for Bazarr |
| ingress.hosts | list | `[]` | Host configuration for the Bazarr ingress |
| ingress.ingressClassName | string | `""` | The ingress class to use for the Bazarr ingress |
| ingress.mainPort | int | `6767` | The main http port to use for the Bazarr ingress |
| ingress.tls | list | `[]` | TLS configuration for the Bazarr ingress |
| media.accessMode | string | `"ReadWriteOnce"` | The access mode to use for the Bazarr media persistent volume claim |
| media.annotations | object | `{}` | Annotations to apply to the Bazarr media persistent volume claim |
| media.enabled | bool | `true` | Whether to enable the creation of a persistent volume claim for the Bazarr media |
| media.existingClaim | string | `""` | Use this attribute to reference an existing persistent volume claim to use for the Bazarr media |
| media.retain | bool | `false` | Whether to keep the persistent volume claim for the media after the Bazarr chart is uninstalled |
| media.size | string | `"50Gi"` | The amount of storage to request for the Bazarr media |
| nameOverride | string | `""` | Optional short name override for the resources |
| namespaceOverride | string | `""` | Optional namespace override for the resources |
| service.annotations | object | `{}` | Annotations to apply to the Bazarr service |
| service.ports | list | `[{"name":"http","port":6767,"protocol":"TCP"}]` | Port to expose the Bazarr service on |
| service.type | string | `"ClusterIP"` | The type of service to create |

----------------------------------------------
Autogenerated from chart metadata using [helm-docs v1.14.2](https://github.com/norwoodj/helm-docs/releases/v1.14.2)
