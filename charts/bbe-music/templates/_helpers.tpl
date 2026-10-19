{{- define "bbe-music.labels" -}}
app.kubernetes.io/name: bbe-music
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{/*
The NAS user the apps write the music as
*/}}
{{- define "bbe-music.runAsUser" -}}
runAsNonRoot: true
runAsUser: {{ .Values.bbe.music.user.uid | int }}
runAsGroup: {{ .Values.bbe.music.user.gid | int }}
{{- end -}}

{{/*
Where things are on the share, mounted whole at /media in every app, as bbe-media mounts it. Moves between them are
renames within one mount, and Lidarr's imports from qBittorrent are hardlinks
*/}}
{{- define "bbe-music.musicDir" -}}/media/music{{- end -}}
{{- define "bbe-music.soulseekDir" -}}/media/downloads/soulseek{{- end -}}

{{/*
The init containers and Jobs that only create folders and copy files
*/}}
{{- define "bbe-music.smallResources" -}}
requests:
  memory: 16Mi
  cpu: 10m
limits:
  memory: 64Mi
{{- end -}}

{{- define "bbe-music.spotifyDir" -}}/media/music-spotify{{- end -}}
