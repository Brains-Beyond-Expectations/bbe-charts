# bbe-observability

![Version: 0.0.1](https://img.shields.io/badge/Version-0.0.1-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square)

Metrics, logs and alerts for the BBE cluster, with Prometheus, Loki, Alloy and Grafana behind single sign-on

**Homepage:** <https://brains-beyond-expectations.github.io/bbe-charts>

## Requirements

| Repository | Name | Version |
|------------|------|---------|
| https://grafana.github.io/helm-charts | alloy | 1.14.2 |
| https://grafana.github.io/helm-charts | loki | 7.5.0 |
| https://kubernetes-sigs.github.io/metrics-server/ | metrics-server | 3.14.0 |
| https://prometheus-community.github.io/helm-charts | kube-prometheus-stack | 92.11.0 |

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| alloy.alloy.configMap.content | string | `"// The pods on this node, each container's log files found from its pod's UID\ndiscovery.kubernetes \"pods\" {\n  role = \"pod\"\n  selectors {\n    role  = \"pod\"\n    field = \"spec.nodeName=\" + sys.env(\"NODE_NAME\")\n  }\n}\n\ndiscovery.relabel \"pods\" {\n  targets = discovery.kubernetes.pods.targets\n\n  rule {\n    source_labels = [\"__meta_kubernetes_namespace\"]\n    target_label  = \"namespace\"\n  }\n  rule {\n    source_labels = [\"__meta_kubernetes_pod_name\"]\n    target_label  = \"pod\"\n  }\n  rule {\n    source_labels = [\"__meta_kubernetes_pod_container_name\"]\n    target_label  = \"container\"\n  }\n  rule {\n    source_labels = [\"__meta_kubernetes_pod_label_app_kubernetes_io_name\"]\n    target_label  = \"app\"\n  }\n  rule {\n    source_labels = [\"__meta_kubernetes_pod_node_name\"]\n    target_label  = \"node\"\n  }\n  rule {\n    source_labels = [\"__meta_kubernetes_pod_uid\", \"__meta_kubernetes_pod_container_name\"]\n    separator     = \"/\"\n    target_label  = \"__path__\"\n    replacement   = \"/var/log/pods/*$1/*.log\"\n  }\n}\n\nlocal.file_match \"pods\" {\n  path_targets = discovery.relabel.pods.output\n}\n\nloki.source.file \"pods\" {\n  targets    = local.file_match.pods.targets\n  forward_to = [loki.process.pods.receiver]\n}\n\n// Containerd writes each line with its time and stream first\nloki.process \"pods\" {\n  stage.cri {}\n  forward_to = [loki.write.loki.receiver]\n}\n\nloki.write \"loki\" {\n  endpoint {\n    url = \"http://bbe-observability-loki:3100/loki/api/v1/push\"\n  }\n}\n"` |  |
| alloy.alloy.extraEnv[0].name | string | `"NODE_NAME"` |  |
| alloy.alloy.extraEnv[0].valueFrom.fieldRef.fieldPath | string | `"spec.nodeName"` |  |
| alloy.alloy.mounts.varlog | bool | `true` |  |
| alloy.alloy.resources.limits.memory | string | `"256Mi"` |  |
| alloy.alloy.resources.requests.cpu | string | `"20m"` |  |
| alloy.alloy.resources.requests.memory | string | `"64Mi"` |  |
| alloy.alloy.securityContext.runAsNonRoot | bool | `false` |  |
| alloy.alloy.securityContext.runAsUser | int | `0` |  |
| alloy.controller.type | string | `"daemonset"` |  |
| alloy.serviceMonitor.enabled | bool | `true` |  |
| bbe.networkPolicy.enabled | bool | `true` | Whether only the package's own pods may reach Prometheus, Alertmanager, Loki and Alloy, and only they and Traefik Grafana. The cluster's network has to enforce NetworkPolicies, which `bbe setup` turns on for the clusters it creates |
| bbe.observability.alerts.receiver | object | `{}` | The receiver alerts are sent to, in Alertmanager's format without its name, such as `{telegram_configs: [{chat_id: 123, bot_token_file: /etc/alertmanager/secrets/bbe-observability-alerts/token}]}`. Alerts are only shown in Grafana while it's empty. See https://prometheus.io/docs/alerting/latest/configuration/#receiver |
| bbe.observability.alerts.repeatInterval | string | `"12h"` | How often an alert that's still firing is sent again |
| bbe.observability.grafana.ingress.enabled | bool | `true` | Whether to serve Grafana at grafana.<domain>, through bbe-networking's Traefik, for admins signed in with authentik |
| bbe.observability.monitors.auth | bool | `true` | Whether to scrape authentik in bbe-auth |
| bbe.observability.monitors.networking | bool | `true` | Whether to scrape Traefik, cert-manager and Blocky in bbe-networking |
| bbe.observability.monitors.storage | bool | `true` | Whether to scrape Longhorn in bbe-storage |
| bbe.observability.rules.certificateExpiryDays | int | `14` | How many days before it expires a certificate is alerted about. cert-manager renews the domain's a third of the way before it expires, so a certificate this close has failed to renew |
| bbe.observability.rules.longhornDiskUsagePercent | int | `85` | How full a Longhorn disk may get, in percent, before it's alerted about |
| global.bbe.domain | string | `"bbe.home.arpa"` | The domain the apps are named under, such as grafana.bbe.home.arpa, the same as bbe-networking's |
| kube-prometheus-stack.alertmanager.alertmanagerSpec.configSecret | string | `"bbe-observability-alertmanager"` |  |
| kube-prometheus-stack.alertmanager.alertmanagerSpec.resources.limits.memory | string | `"128Mi"` |  |
| kube-prometheus-stack.alertmanager.alertmanagerSpec.resources.requests.cpu | string | `"10m"` |  |
| kube-prometheus-stack.alertmanager.alertmanagerSpec.resources.requests.memory | string | `"32Mi"` |  |
| kube-prometheus-stack.alertmanager.alertmanagerSpec.secrets[0] | string | `"bbe-observability-alerts"` |  |
| kube-prometheus-stack.alertmanager.alertmanagerSpec.useExistingSecret | bool | `true` |  |
| kube-prometheus-stack.cleanPrometheusOperatorObjectNames | bool | `true` |  |
| kube-prometheus-stack.defaultRules.rules.windows | bool | `false` |  |
| kube-prometheus-stack.fullnameOverride | string | `"bbe-observability"` |  |
| kube-prometheus-stack.grafana."grafana.ini"."auth.basic".enabled | bool | `false` |  |
| kube-prometheus-stack.grafana."grafana.ini"."auth.proxy".auto_sign_up | bool | `true` |  |
| kube-prometheus-stack.grafana."grafana.ini"."auth.proxy".enabled | bool | `true` |  |
| kube-prometheus-stack.grafana."grafana.ini"."auth.proxy".header_name | string | `"X-authentik-username"` |  |
| kube-prometheus-stack.grafana."grafana.ini"."auth.proxy".header_property | string | `"username"` |  |
| kube-prometheus-stack.grafana."grafana.ini"."auth.proxy".headers | string | `"Email:X-authentik-email Name:X-authentik-name"` |  |
| kube-prometheus-stack.grafana."grafana.ini".analytics.check_for_updates | bool | `false` |  |
| kube-prometheus-stack.grafana."grafana.ini".analytics.reporting_enabled | bool | `false` |  |
| kube-prometheus-stack.grafana."grafana.ini".auth.disable_login_form | bool | `true` |  |
| kube-prometheus-stack.grafana."grafana.ini".auth.disable_signout_menu | bool | `true` |  |
| kube-prometheus-stack.grafana."grafana.ini".server.root_url | string | `"https://grafana.{{ .Values.global.bbe.domain }}"` |  |
| kube-prometheus-stack.grafana."grafana.ini".users.auto_assign_org | bool | `true` |  |
| kube-prometheus-stack.grafana."grafana.ini".users.auto_assign_org_role | string | `"Admin"` |  |
| kube-prometheus-stack.grafana.additionalDataSources[0].access | string | `"proxy"` |  |
| kube-prometheus-stack.grafana.additionalDataSources[0].editable | bool | `false` |  |
| kube-prometheus-stack.grafana.additionalDataSources[0].name | string | `"Loki"` |  |
| kube-prometheus-stack.grafana.additionalDataSources[0].type | string | `"loki"` |  |
| kube-prometheus-stack.grafana.additionalDataSources[0].uid | string | `"loki"` |  |
| kube-prometheus-stack.grafana.additionalDataSources[0].url | string | `"http://bbe-observability-loki:3100"` |  |
| kube-prometheus-stack.grafana.ingress.enabled | bool | `false` |  |
| kube-prometheus-stack.grafana.persistence.enabled | bool | `true` |  |
| kube-prometheus-stack.grafana.persistence.size | string | `"1Gi"` |  |
| kube-prometheus-stack.grafana.persistence.type | string | `"sts"` |  |
| kube-prometheus-stack.grafana.resources.limits.memory | string | `"384Mi"` |  |
| kube-prometheus-stack.grafana.resources.requests.cpu | string | `"20m"` |  |
| kube-prometheus-stack.grafana.resources.requests.memory | string | `"128Mi"` |  |
| kube-prometheus-stack.grafana.sidecar.resources.limits.memory | string | `"128Mi"` |  |
| kube-prometheus-stack.grafana.sidecar.resources.requests.cpu | string | `"5m"` |  |
| kube-prometheus-stack.grafana.sidecar.resources.requests.memory | string | `"32Mi"` |  |
| kube-prometheus-stack.grafana.testFramework.enabled | bool | `false` |  |
| kube-prometheus-stack.kube-state-metrics.resources.limits.memory | string | `"128Mi"` |  |
| kube-prometheus-stack.kube-state-metrics.resources.requests.cpu | string | `"10m"` |  |
| kube-prometheus-stack.kube-state-metrics.resources.requests.memory | string | `"32Mi"` |  |
| kube-prometheus-stack.kubeControllerManager.service.selector.k8s-app | string | `"kube-controller-manager"` |  |
| kube-prometheus-stack.kubeEtcd.service.port | int | `2381` |  |
| kube-prometheus-stack.kubeEtcd.service.selector.k8s-app | string | `"kube-apiserver"` |  |
| kube-prometheus-stack.kubeEtcd.service.targetPort | int | `2381` |  |
| kube-prometheus-stack.kubeProxy.service.selector.k8s-app | string | `"kube-proxy"` |  |
| kube-prometheus-stack.kubeScheduler.service.selector.k8s-app | string | `"kube-scheduler"` |  |
| kube-prometheus-stack.nodeExporter.operatingSystems.aix.enabled | bool | `false` |  |
| kube-prometheus-stack.nodeExporter.operatingSystems.darwin.enabled | bool | `false` |  |
| kube-prometheus-stack.prometheus-node-exporter.resources.limits.memory | string | `"64Mi"` |  |
| kube-prometheus-stack.prometheus-node-exporter.resources.requests.cpu | string | `"10m"` |  |
| kube-prometheus-stack.prometheus-node-exporter.resources.requests.memory | string | `"24Mi"` |  |
| kube-prometheus-stack.prometheus.prometheusSpec.podMonitorSelectorNilUsesHelmValues | bool | `false` |  |
| kube-prometheus-stack.prometheus.prometheusSpec.probeSelectorNilUsesHelmValues | bool | `false` |  |
| kube-prometheus-stack.prometheus.prometheusSpec.resources.limits.memory | string | `"1536Mi"` |  |
| kube-prometheus-stack.prometheus.prometheusSpec.resources.requests.cpu | string | `"100m"` |  |
| kube-prometheus-stack.prometheus.prometheusSpec.resources.requests.memory | string | `"512Mi"` |  |
| kube-prometheus-stack.prometheus.prometheusSpec.retention | string | `"15d"` |  |
| kube-prometheus-stack.prometheus.prometheusSpec.retentionSize | string | `"8GB"` |  |
| kube-prometheus-stack.prometheus.prometheusSpec.ruleSelectorNilUsesHelmValues | bool | `false` |  |
| kube-prometheus-stack.prometheus.prometheusSpec.scrapeConfigSelectorNilUsesHelmValues | bool | `false` |  |
| kube-prometheus-stack.prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues | bool | `false` |  |
| kube-prometheus-stack.prometheus.prometheusSpec.storageSpec.volumeClaimTemplate.spec.accessModes[0] | string | `"ReadWriteOnce"` |  |
| kube-prometheus-stack.prometheus.prometheusSpec.storageSpec.volumeClaimTemplate.spec.resources.requests.storage | string | `"10Gi"` |  |
| kube-prometheus-stack.prometheusOperator.admissionWebhooks.enabled | bool | `false` |  |
| kube-prometheus-stack.prometheusOperator.resources.limits.memory | string | `"256Mi"` |  |
| kube-prometheus-stack.prometheusOperator.resources.requests.cpu | string | `"10m"` |  |
| kube-prometheus-stack.prometheusOperator.resources.requests.memory | string | `"64Mi"` |  |
| kube-prometheus-stack.prometheusOperator.tls.enabled | bool | `false` |  |
| kube-prometheus-stack.windowsMonitoring.enabled | bool | `false` |  |
| loki.backend.replicas | int | `0` |  |
| loki.chunksCache.enabled | bool | `false` |  |
| loki.deploymentMode | string | `"SingleBinary"` |  |
| loki.gateway.enabled | bool | `false` |  |
| loki.loki.auth_enabled | bool | `false` |  |
| loki.loki.commonConfig.replication_factor | int | `1` |  |
| loki.loki.compactor.delete_request_store | string | `"filesystem"` |  |
| loki.loki.compactor.retention_enabled | bool | `true` |  |
| loki.loki.limits_config.retention_period | string | `"360h"` |  |
| loki.loki.schemaConfig.configs[0].from | string | `"2026-01-01"` |  |
| loki.loki.schemaConfig.configs[0].index.period | string | `"24h"` |  |
| loki.loki.schemaConfig.configs[0].index.prefix | string | `"index_"` |  |
| loki.loki.schemaConfig.configs[0].object_store | string | `"filesystem"` |  |
| loki.loki.schemaConfig.configs[0].schema | string | `"v13"` |  |
| loki.loki.schemaConfig.configs[0].store | string | `"tsdb"` |  |
| loki.loki.storage.type | string | `"filesystem"` |  |
| loki.lokiCanary.enabled | bool | `false` |  |
| loki.read.replicas | int | `0` |  |
| loki.resultsCache.enabled | bool | `false` |  |
| loki.sidecar.rules.enabled | bool | `false` |  |
| loki.singleBinary.persistence.size | string | `"10Gi"` |  |
| loki.singleBinary.replicas | int | `1` |  |
| loki.singleBinary.resources.limits.memory | string | `"1Gi"` |  |
| loki.singleBinary.resources.requests.cpu | string | `"50m"` |  |
| loki.singleBinary.resources.requests.memory | string | `"256Mi"` |  |
| loki.test.enabled | bool | `false` |  |
| loki.write.replicas | int | `0` |  |
| metrics-server.args[0] | string | `"--kubelet-insecure-tls"` |  |
| metrics-server.resources.limits.memory | string | `"128Mi"` |  |
| metrics-server.resources.requests.cpu | string | `"10m"` |  |
| metrics-server.resources.requests.memory | string | `"32Mi"` |  |

----------------------------------------------
Autogenerated from chart metadata using [helm-docs v1.14.2](https://github.com/norwoodj/helm-docs/releases/v1.14.2)
