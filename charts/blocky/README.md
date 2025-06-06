# blocky

![Version: 1.1.2](https://img.shields.io/badge/Version-1.1.2-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: v0.26](https://img.shields.io/badge/AppVersion-v0.26-informational?style=flat-square)

A DNS proxy and ad-blocker for the local network

**Homepage:** <https://brains-beyond-expectations.github.io/bbe-charts>

## Source Code

* <https://github.com/0xERR0R/blocky>

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| blocky.annotations | object | `{}` | Annotations to apply to the Blocky pod |
| blocky.image.repository | string | `"ghcr.io/0xerr0r/blocky"` | The image repository to pull from |
| blocky.image.tag | string | `""` | The image tag to pull |
| blocky.livenessProbe | object | `{"exec":{"command":["/app/blocky","healthcheck","--port","53"]},"failureThreshold":6,"initialDelaySeconds":10,"periodSeconds":10,"timeoutSeconds":1}` | The livenessProbe configuration for the Blocky pod |
| blocky.podAntiAffinity | bool | `true` | Whether to enable or disable recommended podAntiAffinity rules |
| blocky.readinessProbe | object | `{"failureThreshold":6,"initialDelaySeconds":10,"periodSeconds":10,"tcpSocket":{"port":"dns-tcp"},"timeoutSeconds":1}` | The readinessProbe configuration for the Blocky pod |
| blocky.replicas | int | `2` | How many replicas of the Blocky pod to run |
| blocky.resources.limits.cpu | string | `""` | The amount of CPU to limit the Blocky pod to |
| blocky.resources.limits.memory | string | `"128Mi"` | The amount of memory to limit the Blocky pod to |
| blocky.resources.requests.cpu | string | `"50m"` | The amount of CPU to request for the Blocky pod |
| blocky.resources.requests.memory | string | `"128Mi"` | The amount of memory to request for the Blocky pod |
| blocky.securityContext.readOnlyRootFilesystem | bool | `true` | Whether to run Blocky with a read-only root filesystem |
| blocky.securityContext.runAsUser | int | `1000` | The user ID to run Blocky as |
| blocky.startupProbe | object | `{"exec":{"command":["/app/blocky","healthcheck","--port","53"]},"failureThreshold":30,"initialDelaySeconds":10,"periodSeconds":10,"timeoutSeconds":1}` | The startupProbe configuration for the Blocky pod |
| blocky.strategyType | string | `"RollingUpdate"` | The strategy to use for updating the Blocky pods |
| config.annotations | object | `{}` | Annotations to apply to the Blocky ConfigMap |
| config.yaml | string | `"upstream:\n  default:\n    - 1.1.1.1\n    - 8.8.8.8\nblocking:\n  blackLists:\n    ads:\n      - https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts\n  clientGroupsBlock:\n    default:\n      - ads\nport: 53\nhttpPort: 4000\ncaching:\n  minTime: 5m\n  maxTime: 30m\nprometheus:\n  enable: true\n"` | The configuration for Blocky |
| fullnameOverride | string | `""` | Optional full name override for the resources |
| metrics.annotations | object | `{}` | Annotations to apply to the Blocky ServiceMonitor |
| metrics.enabled | bool | `false` | Whether to enable the Blocky ServiceMonitor for Prometheus scraping |
| metrics.interval | string | `"30s"` | The interval at which to scrape metrics from Blocky |
| metrics.port | string | `"http"` | The port to use to scrape metrics from Blocky |
| metrics.scrapeTimeout | string | `nil` | The timeout for scraping metrics from Blocky |
| nameOverride | string | `""` | Optional short name override for the resources |
| namespaceOverride | string | `""` | Optional namespace override for the resources |
| service.annotations | object | `{}` | Annotations to apply to the Blocky service |
| service.ports | list | `[{"name":"dns-udp","port":53,"protocol":"UDP"},{"name":"dns-tcp","port":53,"protocol":"TCP"},{"name":"http","port":4000,"protocol":"TCP"}]` | Port to expose the Blocky service on |
| service.type | string | `"LoadBalancer"` | The type of service to create |

----------------------------------------------
Autogenerated from chart metadata using [helm-docs v1.14.2](https://github.com/norwoodj/helm-docs/releases/v1.14.2)
