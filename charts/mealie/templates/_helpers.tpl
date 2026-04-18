{{- define "mealie.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "mealie.fullname" -}}
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

{{- define "mealie.namespace" -}}
{{- if .Values.namespaceOverride }}
{{- .Values.namespaceOverride }}
{{- else }}
{{- .Release.Namespace }}
{{- end }}
{{- end }}

{{- define "mealie.image" -}}
{{- if .Values.mealie.image.tag -}}
{{ .Values.mealie.image.tag }}
{{- else -}}
{{ .Chart.AppVersion }}
{{- end -}}
{{- end -}}

{{/*
Create the env for the container
*/}}
{{- define "mealie.mealieEnv" -}}
{{- $envVars := list }}
{{- if .Values.mealie.env }}
{{- $envVars = concat $envVars .Values.mealie.env }}
{{- end }}
{{- $defaultEnv := list -}}
{{- $defaultEnv = append $defaultEnv (dict "name" "TZ" "value" "UTC") -}}
{{- $envVars = concat $envVars $defaultEnv -}}
{{ toYaml $envVars }}
{{- end -}}

{{/*
Create the envFrom for the container
*/}}
{{- define "mealie.mealieEnvFrom" -}}
{{- $envFrom := list }}
{{- if .Values.mealie.envFrom }}
{{- $envFrom = concat $envFrom .Values.mealie.envFrom }}
{{- end }}
{{- if not (empty $envFrom) -}}
{{ toYaml $envFrom }}
{{- end -}}
{{- end -}}

{{/*
Create the annotations for data PVC
*/}}
{{- define "mealie.dataAnnotations" -}}
{{- $annotations := .Values.data.annotations | default dict -}}
{{- if .Values.data.retain -}}
{{- $annotations = merge $annotations (dict "helm.sh/resource-policy" "keep") -}}
{{- end -}}
{{- if not (empty $annotations) -}}
{{- toYaml $annotations -}}
{{- end -}}
{{- end -}}

{{- define "mealie.dataClaimName" -}}
{{- if .Values.data.existingClaim }}
{{- .Values.data.existingClaim }}
{{- else }}
{{- printf "%s-data" (include "mealie.fullname" .) -}}
{{- end }}
{{- end }}
