{{- define "blocky.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "blocky.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}

{{- define "blocky.image" -}}
{{- if .Values.blocky.image.tag -}}
{{ .Values.blocky.image.tag }}
{{- else -}}
{{ .Chart.AppVersion }}
{{- end -}}
{{- end -}}
