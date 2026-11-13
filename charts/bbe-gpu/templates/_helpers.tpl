{{- define "bbe-gpu.labels" -}}
app.kubernetes.io/name: bbe-gpu
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}
