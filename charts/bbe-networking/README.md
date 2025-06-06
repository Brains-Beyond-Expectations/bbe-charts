# bbe-networking

![Version: 0.2.2](https://img.shields.io/badge/Version-0.2.2-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square)

A collection of charts for BBE cluster networking

**Homepage:** <https://brains-beyond-expectations.github.io/bbe-charts>

## Requirements

| Repository | Name | Version |
|------------|------|---------|
| https://brains-beyond-expectations.github.io/bbe-charts | blocky | 1.1.1 |
| https://kubernetes.github.io/ingress-nginx | ingress-nginx | 4.12.1 |
| https://metallb.github.io/metallb | metallb | 0.14.9 |

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| bbe.metallb.blocky.ipAddressPool | string | `nil` |  |
| ingress-nginx.controller.allowSnippetAnnotations | bool | `true` |  |
| ingress-nginx.controller.config.annotations-risk-level | string | `"Critical"` |  |
| ingress-nginx.controller.config.strict-validate-path-type | bool | `false` |  |
| ingress-nginx.controller.ingressClassResource.controllerValue | string | `"k8s.io/ingress-nginx"` |  |
| ingress-nginx.controller.ingressClassResource.default | bool | `true` |  |
| ingress-nginx.controller.ingressClassResource.enabled | bool | `true` |  |
| ingress-nginx.controller.ingressClassResource.name | string | `"nginx"` |  |
| ingress-nginx.controller.metrics.enabled | bool | `true` |  |
| ingress-nginx.controller.metrics.serviceMonitor.enabled | bool | `true` |  |
| ingress-nginx.controller.service.enabled | bool | `true` |  |
| ingress-nginx.controller.service.loadBalancerIP | string | `nil` |  |
| ingress-nginx.controller.service.type | string | `"LoadBalancer"` |  |
| metallb.speaker.ignoreExcludeLB | bool | `true` |  |

----------------------------------------------
Autogenerated from chart metadata using [helm-docs v1.14.2](https://github.com/norwoodj/helm-docs/releases/v1.14.2)
