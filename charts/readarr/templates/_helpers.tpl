{{- define "readarr.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "readarr.fullname" -}}
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

{{- define "readarr.namespace" -}}
{{- if .Values.namespaceOverride }}
{{- .Values.namespaceOverride }}
{{- else }}
{{- .Release.Namespace }}
{{- end }}
{{- end }}

{{- define "readarr.image" -}}
{{- if .Values.readarr.image.tag -}}
{{ .Values.readarr.image.tag }}
{{- else -}}
{{ .Chart.AppVersion }}
{{- end -}}
{{- end -}}

{{- define "readarr.readarrEnv" -}}
{{- $envVars := list }}
{{- if .Values.readarr.env }}
{{- $envVars = concat $envVars .Values.readarr.env }}
{{- end }}
{{- $defaultEnv := list -}}
{{- $defaultEnv = append $defaultEnv (dict "name" "TZ" "value" "UTC") -}}
{{- $envVars = concat $envVars $defaultEnv -}}
{{ toYaml $envVars }}
{{- end -}}

{{- define "readarr.readarrEnvFrom" -}}
{{- $envFrom := list }}
{{- if .Values.readarr.envFrom }}
{{- $envFrom = concat $envFrom .Values.readarr.envFrom }}
{{- end }}
{{- if not (empty $envFrom) -}}
{{ toYaml $envFrom }}
{{- end -}}
{{- end -}}

{{- define "readarr.configAnnotations" -}}
{{- $annotations := .Values.config.annotations | default dict -}}
{{- if .Values.config.retain -}}
{{- $annotations = merge $annotations (dict "helm.sh/resource-policy" "keep") -}}
{{- end -}}
{{- if not (empty $annotations) -}}
{{- toYaml $annotations -}}
{{- end -}}
{{- end -}}

{{- define "readarr.configClaimName" -}}
{{- if .Values.config.existingClaim }}
{{- .Values.config.existingClaim }}
{{- else }}
{{- printf "%s-config" (include "readarr.fullname" .) -}}
{{- end }}
{{- end }}

{{- define "readarr.booksAnnotations" -}}
{{- $annotations := .Values.books.annotations | default dict -}}
{{- if .Values.books.retain -}}
{{- $annotations = merge $annotations (dict "helm.sh/resource-policy" "keep") -}}
{{- end -}}
{{- if not (empty $annotations) -}}
{{- toYaml $annotations -}}
{{- end -}}
{{- end -}}

{{- define "readarr.booksClaimName" -}}
{{- if .Values.books.existingClaim }}
{{- .Values.books.existingClaim }}
{{- else }}
{{- printf "%s-books" (include "readarr.fullname" .) -}}
{{- end }}
{{- end }}
