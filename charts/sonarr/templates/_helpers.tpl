{{- define "sonarr.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "sonarr.fullname" -}}
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

{{- define "sonarr.namespace" -}}
{{- if .Values.namespaceOverride }}
{{- .Values.namespaceOverride }}
{{- else }}
{{- .Release.Namespace }}
{{- end }}
{{- end }}

{{- define "sonarr.image" -}}
{{- if .Values.sonarr.image.tag -}}
{{ .Values.sonarr.image.tag }}
{{- else -}}
{{ .Chart.AppVersion }}
{{- end -}}
{{- end -}}

{{/*
Create the env for the container
*/}}
{{- define "sonarr.sonarrEnv" -}}
{{- $envVars := list }}
{{- if .Values.sonarr.env }}
{{- $envVars = concat $envVars .Values.sonarr.env }}
{{- end }}
{{- $defaultEnv := list -}}
{{- $defaultEnv = append $defaultEnv (dict "name" "TZ" "value" "UTC") -}}
{{- $defaultEnv = append $defaultEnv (dict "name" "PUID" "value" (printf "%v" .Values.sonarr.securityContext.runAsUser)) -}}
{{- $defaultEnv = append $defaultEnv (dict "name" "PGID" "value" (printf "%v" .Values.sonarr.securityContext.runAsGroup)) -}}
{{- $envVars = concat $envVars $defaultEnv -}}
{{ toYaml $envVars }}
{{- end -}}

{{/*
Create the annotations for config PVC
*/}}
{{- define "sonarr.configAnnotations" -}}
{{- $annotations := .Values.config.annotations | default dict -}}
{{- if .Values.config.retain -}}
{{- $annotations = merge $annotations (dict "helm.sh/resource-policy" "keep") -}}
{{- end -}}
{{- if not (empty $annotations) -}}
{{- toYaml $annotations -}}
{{- end -}}
{{- end -}}

{{- define "sonarr.configClaimName" -}}
{{- if .Values.config.existingClaim }}
{{- .Values.config.existingClaim }}
{{- else }}
{{- printf "%s-config" (include "sonarr.fullname" .) -}}
{{- end }}
{{- end }}

{{/*
Create the annotations for media PVC
*/}}
{{- define "sonarr.mediaAnnotations" -}}
{{- $annotations := .Values.media.annotations | default dict -}}
{{- if .Values.media.retain -}}
{{- $annotations = merge $annotations (dict "helm.sh/resource-policy" "keep") -}}
{{- end -}}
{{- if not (empty $annotations) -}}
{{- toYaml $annotations -}}
{{- end -}}
{{- end -}}

{{- define "sonarr.mediaClaimName" -}}
{{- if .Values.media.existingClaim }}
{{- .Values.media.existingClaim }}
{{- else }}
{{- printf "%s-media" (include "sonarr.fullname" .) -}}
{{- end }}
{{- end }}