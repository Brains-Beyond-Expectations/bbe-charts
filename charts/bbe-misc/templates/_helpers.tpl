{{- define "bbe-misc.labels" -}}
app.kubernetes.io/name: bbe-misc
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{- define "bbe-misc.ldapBaseDn" -}}
dc=ldap,dc=goauthentik,dc=io
{{- end -}}

{{- define "bbe-misc.snipeitUrl" -}}
https://snipeit.{{ .Values.global.bbe.domain }}
{{- end -}}

{{/*
Snipe-IT's settings, shared by the app and its setup, which boots Snipe-IT's own code
*/}}
{{- define "bbe-misc.snipeitEnv" -}}
- name: APP_ENV
  value: production
- name: APP_DEBUG
  value: "false"
- name: APP_KEY
  valueFrom:
    secretKeyRef:
      name: bbe-misc-snipeit
      key: app-key
- name: APP_URL
  value: {{ include "bbe-misc.snipeitUrl" . }}
- name: APP_TIMEZONE
  value: {{ .Values.bbe.misc.snipeit.timezone | quote }}
# Snipe-IT points every link at APP_URL and refuses other names unless this is set. It's also reached at its public
# name through bbe-tunnel, and Traefik only passes on the names it has routes for
- name: APP_ALLOW_INSECURE_HOSTS
  value: "true"
# Traefik, from the pod network
- name: APP_TRUSTED_PROXIES
  value: 10.0.0.0/8,172.16.0.0/12,192.168.0.0/16
- name: SECURE_COOKIES
  value: "true"
# Its LDAP settings page refuses to test a server on a private address otherwise, and authentik's is in the cluster
- name: TEST_ALLOW_PRIVATE_IPS
  value: "true"
- name: DB_CONNECTION
  value: mariadb
- name: DB_HOST
  value: bbe-misc-mariadb
- name: DB_PORT
  value: "3306"
- name: DB_DATABASE
  value: snipeit
- name: DB_USERNAME
  value: snipeit
- name: DB_PASSWORD
  valueFrom:
    secretKeyRef:
      name: bbe-misc-mariadb
      key: password
# No mail server is set up, so mail is written to its log rather than failing
- name: MAIL_MAILER
  value: log
{{- end -}}
