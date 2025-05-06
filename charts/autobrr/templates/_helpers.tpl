{{- define "autobrr.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "autobrr.fullname" -}}
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

{{- define "autobrr.namespace" -}}
{{- if .Values.namespaceOverride }}
{{- .Values.namespaceOverride }}
{{- else }}
{{- .Release.Namespace }}
{{- end }}
{{- end }}

{{- define "autobrr.image" -}}
{{- if .Values.autobrr.image.tag -}}
{{ .Values.autobrr.image.tag }}
{{- else -}}
{{ .Chart.AppVersion }}
{{- end -}}
{{- end -}}

{{/*
Create the env for the container
*/}}
{{- define "autobrr.autobrrEnv" -}}
{{- $envVars := list }}
{{- if .Values.autobrr.env }}
{{- $envVars = concat $envVars .Values.autobrr.env }}
{{- end }}
{{- $defaultEnv := list -}}
{{- $defaultEnv = append $defaultEnv (dict "name" "TZ" "value" "UTC") -}}
{{- $envVars = concat $envVars $defaultEnv -}}
{{ toYaml $envVars }}
{{- end -}}

{{/*
Create the annotations for config PVC
*/}}
{{- define "autobrr.configAnnotations" -}}
{{- $annotations := .Values.config.annotations | default dict -}}
{{- if .Values.config.retain -}}
{{- $annotations = merge $annotations (dict "helm.sh/resource-policy" "keep") -}}
{{- end -}}
{{- if not (empty $annotations) -}}
{{- toYaml $annotations -}}
{{- end -}}
{{- end -}}

{{- define "autobrr.configClaimName" -}}
{{- if .Values.config.existingClaim }}
{{- .Values.config.existingClaim }}
{{- else }}
{{- printf "%s-config" (include "autobrr.fullname" .) -}}
{{- end }}
{{- end }}
