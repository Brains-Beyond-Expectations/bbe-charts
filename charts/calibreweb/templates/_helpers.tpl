{{- define "calibreweb.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "calibreweb.fullname" -}}
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

{{- define "calibreweb.namespace" -}}
{{- if .Values.namespaceOverride }}
{{- .Values.namespaceOverride }}
{{- else }}
{{- .Release.Namespace }}
{{- end }}
{{- end }}

{{- define "calibreweb.image" -}}
{{- if .Values.calibreWeb.image.tag -}}
{{ .Values.calibreWeb.image.tag }}
{{- else -}}
{{ .Chart.AppVersion }}
{{- end -}}
{{- end -}}

{{- define "calibreweb.calibreWebEnv" -}}
{{- $envVars := list }}
{{- if .Values.calibreWeb.env }}
{{- $envVars = concat $envVars .Values.calibreWeb.env }}
{{- end }}
{{- $defaultEnv := list -}}
{{- $defaultEnv = append $defaultEnv (dict "name" "TZ" "value" "UTC") -}}
{{- $envVars = concat $envVars $defaultEnv -}}
{{ toYaml $envVars }}
{{- end -}}

{{- define "calibreweb.calibreWebEnvFrom" -}}
{{- $envFrom := list }}
{{- if .Values.calibreWeb.envFrom }}
{{- $envFrom = concat $envFrom .Values.calibreWeb.envFrom }}
{{- end }}
{{- if not (empty $envFrom) -}}
{{ toYaml $envFrom }}
{{- end -}}
{{- end -}}

{{- define "calibreweb.configAnnotations" -}}
{{- $annotations := .Values.config.annotations | default dict -}}
{{- if .Values.config.retain -}}
{{- $annotations = merge $annotations (dict "helm.sh/resource-policy" "keep") -}}
{{- end -}}
{{- if not (empty $annotations) -}}
{{- toYaml $annotations -}}
{{- end -}}
{{- end -}}

{{- define "calibreweb.configClaimName" -}}
{{- if .Values.config.existingClaim }}
{{- .Values.config.existingClaim }}
{{- else }}
{{- printf "%s-config" (include "calibreweb.fullname" .) -}}
{{- end }}
{{- end }}

{{- define "calibreweb.booksAnnotations" -}}
{{- $annotations := .Values.books.annotations | default dict -}}
{{- if .Values.books.retain -}}
{{- $annotations = merge $annotations (dict "helm.sh/resource-policy" "keep") -}}
{{- end -}}
{{- if not (empty $annotations) -}}
{{- toYaml $annotations -}}
{{- end -}}
{{- end -}}

{{- define "calibreweb.booksClaimName" -}}
{{- if .Values.books.existingClaim }}
{{- .Values.books.existingClaim }}
{{- else }}
{{- printf "%s-books" (include "calibreweb.fullname" .) -}}
{{- end }}
{{- end }}
