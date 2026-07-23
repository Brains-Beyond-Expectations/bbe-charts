{{/*
Name helpers for the prowlarr component embedded in bbe-media.
The deployment name is always "{release}-prowlarr" so the lookup
in bbe-library can find it deterministically.
*/}}

{{- define "bbe-media.prowlarr.name" -}}
prowlarr
{{- end -}}

{{- define "bbe-media.prowlarr.fullname" -}}
{{- printf "%s-prowlarr" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "bbe-media.prowlarr.namespace" -}}
{{- .Release.Namespace -}}
{{- end -}}

{{- define "bbe-media.prowlarr.image" -}}
{{- if .Values.prowlarr.image.tag -}}
{{ .Values.prowlarr.image.tag }}
{{- else -}}
latest
{{- end -}}
{{- end -}}

{{- define "bbe-media.prowlarr.env" -}}
{{- $envVars := list }}
{{- if .Values.prowlarr.env }}
{{- $envVars = concat $envVars .Values.prowlarr.env }}
{{- end }}
{{- $defaultEnv := list -}}
{{- $defaultEnv = append $defaultEnv (dict "name" "TZ" "value" "UTC") -}}
{{- $defaultEnv = append $defaultEnv (dict "name" "PUID" "value" (printf "%v" .Values.prowlarr.securityContext.runAsUser)) -}}
{{- $defaultEnv = append $defaultEnv (dict "name" "PGID" "value" (printf "%v" .Values.prowlarr.securityContext.runAsGroup)) -}}
{{- $envVars = concat $envVars $defaultEnv -}}
{{ toYaml $envVars }}
{{- end -}}

{{- define "bbe-media.prowlarr.configAnnotations" -}}
{{- $annotations := .Values.prowlarrConfig.annotations | default dict -}}
{{- if .Values.prowlarrConfig.retain -}}
{{- $annotations = merge $annotations (dict "helm.sh/resource-policy" "keep") -}}
{{- end -}}
{{- if not (empty $annotations) -}}
{{- toYaml $annotations -}}
{{- end -}}
{{- end -}}

{{- define "bbe-media.prowlarr.configClaimName" -}}
{{- if .Values.prowlarrConfig.existingClaim -}}
{{- .Values.prowlarrConfig.existingClaim -}}
{{- else -}}
{{- printf "%s-prowlarr-config" .Release.Name -}}
{{- end -}}
{{- end -}}
