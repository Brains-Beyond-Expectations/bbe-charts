{{/*
MetalLB takes addresses as a CIDR or a range, so a single IP becomes a CIDR holding only that IP
*/}}
{{- define "bbe-networking.addresses" -}}
{{- $addresses := toString . | trim -}}
{{- if or (contains "/" $addresses) (contains "-" $addresses) -}}
{{- $addresses -}}
{{- else if contains ":" $addresses -}}
{{- printf "%s/128" $addresses -}}
{{- else -}}
{{- printf "%s/32" $addresses -}}
{{- end -}}
{{- end -}}
