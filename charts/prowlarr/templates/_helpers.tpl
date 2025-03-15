{{- define "prowlarr.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "prowlarr.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{- define "prowlarr.namespace" -}}
{{- if .Values.namespaceOverride }}
{{- .Values.namespaceOverride }}
{{- else }}
{{- .Release.Namespace }}
{{- end }}
{{- end }}

{{- define "prowlarr.image" -}}
{{- if .Values.prowlarr.image.tag -}}
{{ .Values.prowlarr.image.tag }}
{{- else -}}
{{ .Chart.AppVersion }}
{{- end -}}
{{- end -}}

{{/*
Create the annotations for config PVC
*/}}
{{- define "prowlarr.configAnnotations" -}}
{{- $annotations := .Values.config.annotations | default dict -}}
{{- if .Values.config.retain -}}
{{- $annotations = merge $annotations (dict "helm.sh/resource-policy" "keep") -}}
{{- end -}}
{{- if not (empty $annotations) -}}
{{- toYaml $annotations -}}
{{- end -}}
{{- end -}}

{{- define "prowlarr.configClaimName" -}}
{{- if .Values.config.existingClaim }}
{{- .Values.config.existingClaim }}
{{- else }}
{{- printf "%s-config" (include "prowlarr.fullname" .) -}}
{{- end }}
{{- end }}

{{/*
Create the annotations for media PVC
*/}}
{{- define "prowlarr.mediaAnnotations" -}}
{{- $annotations := .Values.media.annotations | default dict -}}
{{- if .Values.media.retain -}}
{{- $annotations = merge $annotations (dict "helm.sh/resource-policy" "keep") -}}
{{- end -}}
{{- if not (empty $annotations) -}}
{{- toYaml $annotations -}}
{{- end -}}
{{- end -}}

{{- define "prowlarr.mediaClaimName" -}}
{{- if .Values.media.existingClaim }}
{{- .Values.media.existingClaim }}
{{- else }}
{{- printf "%s-media" (include "prowlarr.fullname" .) -}}
{{- end }}
{{- end }}