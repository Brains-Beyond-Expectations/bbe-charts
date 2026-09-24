{{- define "bbe-media.labels" -}}
app.kubernetes.io/name: bbe-media
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{/*
Volumes aren't namespaced, so the namespace keeps the library's volume name unique in the cluster
*/}}
{{- define "bbe-media.libraryVolumeName" -}}
{{- printf "%s-bbe-media-library" .Release.Namespace | trunc 63 | trimSuffix "-" -}}
{{- end -}}
