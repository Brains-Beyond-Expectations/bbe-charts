# mealie

![Version: 0.1.0](https://img.shields.io/badge/Version-0.1.0-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: v2.3.0](https://img.shields.io/badge/AppVersion-v2.3.0-informational?style=flat-square)

A self-hosted recipe manager and meal planner with a rich UI.

**Homepage:** <https://brains-beyond-expectations.github.io/bbe-charts>

## Source Code

* <https://github.com/mealie-recipes/mealie>

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| data.accessMode | string | `"ReadWriteOnce"` | The access mode to use for the Mealie data persistent volume claim |
| data.annotations | object | `{}` | Annotations to apply to the Mealie data persistent volume claim |
| data.enabled | bool | `true` | Whether to enable the creation of a persistent volume claim for Mealie data |
| data.existingClaim | string | `""` | Use this attribute to reference an existing persistent volume claim for Mealie data |
| data.retain | bool | `false` | Whether to keep the persistent volume claim after the Mealie chart is uninstalled |
| data.size | string | `"5Gi"` | The amount of storage to request for the Mealie data volume |
| fullnameOverride | string | `""` | Optional full name override for the resources |
| ingress.annotations | object | `{}` | Annotations to apply to the Mealie ingress |
| ingress.enabled | bool | `false` | Whether to create an ingress for Mealie |
| ingress.hosts | list | `[]` | Host configuration for the Mealie ingress |
| ingress.ingressClassName | string | `""` | The ingress class to use for the Mealie ingress |
| ingress.mainPort | int | `9000` | The main http port to use for the Mealie ingress |
| ingress.tls | list | `[]` | TLS configuration for the Mealie ingress |
| mealie.annotations | object | `{}` | Annotations to apply to the Mealie pod |
| mealie.env | list | `[]` | The environment variables to set for the Mealie pod |
| mealie.envFrom | list | `[]` | The environment variables to set for the Mealie pod from a config map or secret |
| mealie.image.repository | string | `"ghcr.io/mealie-recipes/mealie"` | The image repository to pull from |
| mealie.image.tag | string | `""` | The image tag to pull (defaults to Chart appVersion) |
| mealie.livenessProbe | object | `{"failureThreshold":5,"initialDelaySeconds":60,"periodSeconds":10,"tcpSocket":{"port":9000},"timeoutSeconds":1}` | The livenessProbe configuration for the Mealie pod |
| mealie.readinessProbe | object | `{"failureThreshold":3,"periodSeconds":10,"tcpSocket":{"port":9000},"timeoutSeconds":1}` | The readinessProbe configuration for the Mealie pod |
| mealie.replicas | int | `1` | How many replicas of the Mealie pod to run |
| mealie.resources.limits.cpu | string | `""` | The amount of CPU to limit the Mealie pod to |
| mealie.resources.limits.memory | string | `"512Mi"` | The amount of memory to limit the Mealie pod to |
| mealie.resources.requests.cpu | string | `"50m"` | The amount of CPU to request for the Mealie pod |
| mealie.resources.requests.memory | string | `"256Mi"` | The amount of memory to request for the Mealie pod |
| mealie.securityContext.readOnlyRootFilesystem | bool | `false` | Whether to run Mealie with a read-only root filesystem |
| mealie.securityContext.runAsGroup | int | `0` | The group ID to run Mealie as |
| mealie.securityContext.runAsUser | int | `0` | The user ID to run Mealie as |
| mealie.startupProbe | object | `{"failureThreshold":30,"periodSeconds":5,"tcpSocket":{"port":9000},"timeoutSeconds":1}` | The startupProbe configuration for the Mealie pod |
| mealie.strategyType | string | `"Recreate"` | The strategy to use for updating the Mealie pods |
| nameOverride | string | `""` | Optional short name override for the resources |
| namespaceOverride | string | `""` | Optional namespace override for the resources |
| service.annotations | object | `{}` | Annotations to apply to the Mealie service |
| service.ports | list | `[{"name":"http","port":9000,"protocol":"TCP"}]` | Port to expose the Mealie service on |
| service.type | string | `"ClusterIP"` | The service type for the Mealie service |
