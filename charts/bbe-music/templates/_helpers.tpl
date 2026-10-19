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

{{- define "bbe-music.soulsyncLidarrDir" -}}/media/downloads/soulsync-lidarr{{- end -}}

{{/*
gluetun, the VPN every byte of a pod's internet traffic goes through, as a native sidecar: it starts before the pod's
own containers, once the tunnel and its DNS are up, and stays up next to them. Its firewall is the kill switch: only
the VPN server and the cluster are reachable outside the tunnel, also while the tunnel or gluetun itself restarts.
Takes the chart's context as `root`, the ports the cluster reaches
the pod on as `inputPorts`, the Secret holding gluetun's control server role as `controlSecret`, and optionally
`qbittorrent` (give qBittorrent the forwarded port and the tunnel to bind to) and `volumeMounts`
*/}}
{{- define "bbe.gluetun" -}}
{{- $vpn := .root.Values.global.bbe.vpn -}}
- name: gluetun
  image: {{ $vpn.image }}
  restartPolicy: Always
  command:
    - /bin/sh
    - -c
    # The pod's resolv.conf is shared and gluetun rewrites it, so after gluetun restarts it would find itself there
    # rather than the cluster's DNS, which it sends cluster names to. A stale WireGuard rule stops it from starting
    - |
      if ! grep -q '^nameserver {{ $vpn.clusterDns }}$' /etc/resolv.conf; then
        rest="$(grep -v '^nameserver ' /etc/resolv.conf)"
        printf 'nameserver {{ $vpn.clusterDns }}\n%s\n' "$rest" > /etc/resolv.conf
      fi
      ip rule del table 51820 2>/dev/null || true
      ip -6 rule del table 51820 2>/dev/null || true
      exec /gluetun-entrypoint
  env:
    - name: VPN_SERVICE_PROVIDER
      value: {{ $vpn.provider | quote }}
    - name: VPN_TYPE
      value: wireguard
    # The node's kernel WireGuard, which fails rather than falling back to a userspace one
    - name: WIREGUARD_IMPLEMENTATION
      value: kernelspace
    - name: WIREGUARD_PRIVATE_KEY_SECRETFILE
      value: /secrets/vpn/wireguard_private_key
    {{- with $vpn.serverCountries }}
    - name: SERVER_COUNTRIES
      value: {{ . | quote }}
    {{- end }}
    # Peers reach the app through a port the VPN forwards, which changes when the tunnel reconnects
    - name: VPN_PORT_FORWARDING
      value: "on"
    {{- if .qbittorrent }}
    # qBittorrent listens on the forwarded port and only sends through the tunnel, a second guard next to the
    # firewall. When the tunnel goes down it binds to nothing reachable. gluetun fills in {{ "{{PORT}}" }} itself
    - name: VPN_PORT_FORWARDING_UP_COMMAND
      value: '/bin/sh /scripts/qbittorrent-port.sh {{ "{{PORT}}" }} {{ "{{VPN_INTERFACE}}" }}'
    - name: VPN_PORT_FORWARDING_DOWN_COMMAND
      value: "/bin/sh /scripts/qbittorrent-port.sh '' lo"
    {{- end }}
    # The cluster, outside the tunnel: Services, other pods and its DNS
    - name: FIREWALL_OUTBOUND_SUBNETS
      value: "{{ $vpn.podSubnet }},{{ $vpn.serviceSubnet }}"
    - name: FIREWALL_INPUT_PORTS
      value: {{ .inputPorts | quote }}
    # Its control server, which only the pod reaches, tells the app the forwarded port
    - name: HTTP_CONTROL_SERVER_ADDRESS
      value: "127.0.0.1:8000"
    - name: HTTP_CONTROL_SERVER_AUTH_DEFAULT_ROLE
      valueFrom:
        secretKeyRef:
          name: {{ .controlSecret }}
          key: control-role
    - name: HEALTH_RESTART_VPN
      value: "on"
  # The pod's own containers start once the tunnel is up and cluster names resolve
  startupProbe:
    exec:
      command:
        - /bin/sh
        - -c
        - /gluetun-entrypoint healthcheck && nslookup kubernetes.default.svc.cluster.local 127.0.0.1 >/dev/null
    periodSeconds: 3
    timeoutSeconds: 10
    failureThreshold: 100
  resources:
    requests:
      memory: 32Mi
      cpu: 10m
    limits:
      memory: 256Mi
  # It runs as root, changing the pod's network, which `baseline` doesn't allow
  securityContext:
    runAsUser: 0
    runAsNonRoot: false
    capabilities:
      add:
        - NET_ADMIN
  volumeMounts:
    - name: vpn-key
      mountPath: /secrets/vpn
      readOnly: true
    - name: vpn-rules
      mountPath: /iptables
      readOnly: true
    {{- with .volumeMounts }}
    {{- toYaml . | nindent 4 }}
    {{- end }}
{{- end -}}

{{/*
The files gluetun reads besides its key: firewall rules it adds last. Packets carrying the tunnel's address can briefly
leave by the pod's own interface while gluetun 3.41.3 takes a tunnel down, so anything leaving by it from outside the
cluster is dropped
*/}}
{{- define "bbe.gluetunRules" -}}
post-rules.txt: |
  iptables -I OUTPUT -o eth0 ! -s {{ .Values.global.bbe.vpn.podSubnet }} -j DROP
{{- end -}}
