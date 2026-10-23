{{- define "bbe-auth.labels" -}}
app.kubernetes.io/name: bbe-auth
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{/*
The people the setup creates: the first admin, then those `bbe configure` added. The first admin's password is
projected into the passwords folder as `first-admin`
*/}}
{{- define "bbe-auth.users" -}}
{{- $admin := dict "username" .Values.bbe.auth.admin.username "email" .Values.bbe.auth.admin.email "groups" (list "admins") "secretFields" (dict "password" "first-admin") -}}
{{- prepend (.Values.bbe.auth.users | default list) $admin | toJson -}}
{{- end -}}
