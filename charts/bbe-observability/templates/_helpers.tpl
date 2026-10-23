{{- define "bbe-observability.labels" -}}
app.kubernetes.io/name: bbe-observability
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{/*
Labels Prometheus finds this chart's ServiceMonitors, PodMonitors and rules by. It finds them in every namespace, so
these only tell them apart from other charts'
*/}}
{{- define "bbe-observability.monitorLabels" -}}
{{ include "bbe-observability.labels" . }}
app.kubernetes.io/component: monitoring
{{- end -}}
