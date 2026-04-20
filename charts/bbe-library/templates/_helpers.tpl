{{/*
Name helpers for the prowlarr component embedded in bbe-library.
The deployment name is always "{release}-prowlarr" so the lookup
in bbe-media can find it deterministically.
*/}}

{{- define "bbe-library.prowlarr.name" -}}
prowlarr
{{- end -}}

{{- define "bbe-library.prowlarr.fullname" -}}
{{- printf "%s-prowlarr" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "bbe-library.prowlarr.namespace" -}}
{{- .Release.Namespace -}}
{{- end -}}

{{- define "bbe-library.prowlarr.image" -}}
{{- if .Values.prowlarr.image.tag -}}
{{ .Values.prowlarr.image.tag }}
{{- else -}}
latest
{{- end -}}
{{- end -}}

{{- define "bbe-library.prowlarr.env" -}}
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

{{- define "bbe-library.prowlarr.configAnnotations" -}}
{{- $annotations := .Values.prowlarrConfig.annotations | default dict -}}
{{- if .Values.prowlarrConfig.retain -}}
{{- $annotations = merge $annotations (dict "helm.sh/resource-policy" "keep") -}}
{{- end -}}
{{- if not (empty $annotations) -}}
{{- toYaml $annotations -}}
{{- end -}}
{{- end -}}

{{- define "bbe-library.prowlarr.configClaimName" -}}
{{- if .Values.prowlarrConfig.existingClaim -}}
{{- .Values.prowlarrConfig.existingClaim -}}
{{- else -}}
{{- printf "%s-prowlarr-config" .Release.Name -}}
{{- end -}}
{{- end -}}

{{- define "bbe-library.library.claimName" -}}
{{- printf "%s-library" .Release.Name -}}
{{- end -}}

{{- define "bbe-library.library.annotations" -}}
{{- $annotations := .Values.library.annotations | default dict -}}
{{- if .Values.library.retain -}}
{{- $annotations = merge $annotations (dict "helm.sh/resource-policy" "keep") -}}
{{- end -}}
{{- if not (empty $annotations) -}}
{{- toYaml $annotations -}}
{{- end -}}
{{- end -}}
