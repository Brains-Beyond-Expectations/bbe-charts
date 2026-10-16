{{- define "bbe-library.labels" -}}
app.kubernetes.io/name: bbe-library
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{/*
Volumes aren't namespaced, so the namespace keeps the volumes' names unique in the cluster
*/}}
{{- define "bbe-library.booksVolumeName" -}}
{{- printf "%s-bbe-library-books" .Release.Namespace | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "bbe-library.downloadsVolumeName" -}}
{{- printf "%s-bbe-library-downloads" .Release.Namespace | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
bbe-media's media library volume, whose NFS share qBittorrent downloads to. Shelfmark mounts the same share where
qBittorrent does, as it finds a finished download by the path qBittorrent reports
*/}}
{{- define "bbe-library.mediaVolume" -}}
{{- (lookup "v1" "PersistentVolume" "" "bbe-media-bbe-media-library") | default dict | toJson -}}
{{- end -}}

{{/*
The NAS user the apps write the books as, which bbe-library also runs its init containers as
*/}}
{{- define "bbe-library.runAsUser" -}}
runAsNonRoot: true
runAsUser: {{ .Values.bbe.library.user.uid | int }}
runAsGroup: {{ .Values.bbe.library.user.gid | int }}
{{- end -}}

{{- define "bbe-library.ldapBaseDn" -}}
dc=ldap,dc=goauthentik,dc=io
{{- end -}}

{{/*
The init containers only create folders and copy a file
*/}}
{{- define "bbe-library.initResources" -}}
requests:
  memory: 16Mi
  cpu: 10m
limits:
  memory: 64Mi
{{- end -}}
