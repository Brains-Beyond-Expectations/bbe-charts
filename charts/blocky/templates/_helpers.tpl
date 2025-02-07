{{- define "blocky.hardcodedValues" -}}
controllers:
  main:
    containers:
      blocky:
        image:
          repository: ghcr.io/0xerr0r/blocky
          tag: {{ .Chart.AppVersion }}
        securityContext:
          runAsUser: 1000
          readOnlyRootFilesystem: true

defaultPodOptions:
  affinity:
    podAntiAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
        - weight: 100
          podAffinityTerm:
            labelSelector:
              matchLabels:
                app.kubernetes.io/name: blocky
            topologyKey: kubernetes.io/hostname

persistence:
  config:
    name: {{ .Release.Name }}-config
    enabled: true
    type: configMap
    advancedMounts:
      main:
        blocky:
          - path: /app/config.yml
            subPath: config.yml
{{- end -}}
