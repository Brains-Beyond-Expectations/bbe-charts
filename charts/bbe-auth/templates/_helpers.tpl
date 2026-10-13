{{- define "bbe-auth.labels" -}}
app.kubernetes.io/name: bbe-auth
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{/*
The users the setup creates: the first admin, then those `bbe configure` added. The first admin's password is
projected into the passwords folder as `first-admin`
*/}}
{{- define "bbe-auth.users" -}}
{{- $admin := dict "username" .Values.bbe.auth.admin.username "email" .Values.bbe.auth.admin.email "groups" (list "admins") "secretFields" (dict "password" "first-admin") -}}
{{- prepend (.Values.bbe.auth.users | default list) $admin | toJson -}}
{{- end -}}

{{/*
The clients the setup creates, with the addresses they're reached at under the domain. oauth2-proxy is always one of
them, for the apps behind it
*/}}
{{- define "bbe-auth.clients" -}}
{{- $domain := .Values.global.bbe.domain -}}
{{- $clients := list (dict "clientId" "oauth2-proxy" "name" "bbe apps" "rootUrl" (printf "https://auth.%s" $domain) "redirectUris" (list (printf "https://auth.%s/oauth2/callback" $domain)) "audience" true) -}}
{{- range .Values.bbe.auth.clients -}}
{{- $root := printf "https://%s.%s" .host $domain -}}
{{- $clients = append $clients (dict "clientId" .clientId "name" (.name | default .clientId) "rootUrl" $root "baseUrl" "/" "redirectUris" (list (printf "%s%s" $root .redirectPath))) -}}
{{- end -}}
{{- $clients | toJson -}}
{{- end -}}
