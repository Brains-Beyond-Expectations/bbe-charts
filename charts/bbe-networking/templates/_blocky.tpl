{{/*
Blocky's configuration, from global.bbe.dns. Blocky's chart renders it in its own context, where the parent's values
are only seen through .Values.global
*/}}
{{- define "bbe-networking.blockyConfig" -}}
{{- $bbe := .Values.global.bbe -}}
{{- $dns := $bbe.dns -}}
{{- $blocking := $dns.blocking -}}
{{- /* Only the groups some device gets are loaded, so a group nobody uses costs nothing */ -}}
{{- $used := $blocking.groups | default list -}}
{{- range $client, $groups := $blocking.clients }}
{{- $used = concat $used ($groups | default list) -}}
{{- end }}
{{- range $group := $used }}
{{- if not (hasKey $blocking.lists $group) }}
{{- fail (printf "global.bbe.dns.blocking: no lists for the group %q, which is one of %s" $group (keys $blocking.lists | sortAlpha | join ", ")) }}
{{- end }}
{{- end }}
{{- $lists := dict -}}
{{- range $group, $sources := $blocking.lists }}
{{- if and $sources (has $group $used) }}
{{- $_ := set $lists $group $sources -}}
{{- end }}
{{- end -}}
upstreams:
  groups:
    default:
      {{- toYaml $dns.upstreams | nindent 6 }}
  # Asks the two fastest, and answers with the first reply
  strategy: parallel_best
  timeout: 2s
  # Answers straight away, even if an upstream doesn't answer yet
  init:
    strategy: fast
bootstrapDns:
  {{- toYaml $dns.bootstrap | nindent 2 }}
customDNS:
  mapping:
    {{ $bbe.domain }}: {{ $bbe.ingress.loadBalancerIP }}
    {{- range $name, $address := $dns.records }}
    {{ $name }}: {{ $address }}
    {{- end }}
{{- with $dns.forward }}
conditional:
  mapping:
    {{- toYaml . | nindent 4 }}
{{- end }}
blocking:
  denylists:
    {{- range $group, $sources := $lists }}
    {{ $group }}:
      {{- toYaml $sources | nindent 6 }}
    {{- end }}
  {{- if and $blocking.allowed $lists }}
  # Every group that blocks allows the same domains, each with everything under it. Blocky would block everything
  # else for a device whose groups only allow
  allowlists:
    {{- range $group, $_ := $lists }}
    {{ $group }}:
      - |
        {{- range $allowed := $blocking.allowed }}
        {{ ternary $allowed (printf "*.%s" (trimPrefix "*." $allowed)) (hasPrefix "/" $allowed) }}
        {{- end }}
    {{- end }}
  {{- end }}
  clientGroupsBlock:
    default:
      {{- toYaml ($blocking.groups | default list) | nindent 6 }}
    {{- range $client, $groups := $blocking.clients }}
    {{ $client | quote }}:
      {{- toYaml ($groups | default list) | nindent 6 }}
    {{- end }}
  # Blocked names get 0.0.0.0, which fails at once rather than timing out
  blockType: zeroIp
  blockTTL: {{ $blocking.blockTTL }}
  loading:
    refreshPeriod: {{ $blocking.refreshPeriod }}
    downloads:
      timeout: 60s
      attempts: 5
      cooldown: 10s
    # Answers straight away and blocks once the lists are in, so the house keeps its DNS while they download, and
    # when a list can't be reached
    strategy: fast
caching:
  minTime: 5m
  maxTime: 30m
  # Asks again before a name that's often looked up runs out
  prefetching: true
rebindingProtection:
  enable: {{ $dns.rebindingProtection.enabled }}
  {{- with $dns.rebindingProtection.allowedDomains }}
  allowedDomains:
    {{- toYaml . | nindent 4 }}
  {{- end }}
# Tells devices why a name was blocked, with an Extended DNS Error
ede:
  enable: true
queryLog:
  type: {{ $dns.queryLog }}
ports:
  dns: 53
  http: 4000
prometheus:
  enable: true
{{- end -}}
